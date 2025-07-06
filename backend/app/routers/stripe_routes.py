import stripe
import time

from uuid import UUID
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request
from fastapi import Depends,status
from fastapi.security import OAuth2PasswordBearer

from sqlmodel import Session, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import func

from app.utils.stripe import create_checkout_session,cancel_stripe_subscription
from app.config import STRIPE_WEBHOOK_SECRET,PREMIUM_PRICE_ID,PAYG_PRICE_ID
from app.schemas import CheckoutRequest
from app.dependencies import get_db
from app.auth import get_user_from_token
from app.crud import update_user_subscription
from app.db.models.models import Subscription,SubscriptionStatus,Bot, PlanEnum, SubscriptionHistory
from app.config import MESSAGE_PRICE_ID, BOT_PRICE_ID
from app.utils.payg import report_usage

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

PRICE_IDS = {
    "premium": PREMIUM_PRICE_ID,
    "payg": PAYG_PRICE_ID
}
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(prefix="/stripe", tags=["Stripe"])

@router.post("/create-checkout-session")
async def create_session(
    data: CheckoutRequest, 
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
):
    user = await get_user_from_token(token, db, credentials_exception)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_id = user.id

    try:
        print(f"[create_session] Début pour user_id={user_id}, plan={data.plan}")

        # 1. Vérifier s'il a déjà un abonnement actif du même type
        stmt = select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.plan == data.plan,
            Subscription.status == SubscriptionStatus.active
        )
        result = await db.execute(stmt)
        active_subscription = result.scalars().first()
        if active_subscription:
            print(f"[create_session] Abonnement actif trouvé: {active_subscription.id}")
            raise HTTPException(status_code=400, detail="You already have an active subscription of this type.")

        # 2. Chercher dans l'historique un abonnement identique (plan) pour pouvoir le reprendre
        stmt = select(SubscriptionHistory).where(
            SubscriptionHistory.user_id == user_id,
            SubscriptionHistory.plan == data.plan
        ).order_by(SubscriptionHistory.recorded_at.desc())  # prendre le plus récent
        result = await db.execute(stmt)
        last_history = result.scalars().first()

        if last_history and last_history.stripe_subscription_id:
            print(f"[create_session] Historique trouvé avec subscription_id Stripe: {last_history.stripe_subscription_id}")

            # Récupération de l’abonnement Stripe avant modification
            sub = stripe.Subscription.retrieve(last_history.stripe_subscription_id)
            print(f"[create_session] Etat avant modification : pause_collection={sub.get('pause_collection')}, status={sub.get('status')}")

            # 1. Lever la pause d'abord
            sub_mod = stripe.Subscription.modify(
                last_history.stripe_subscription_id,
                pause_collection=""
            )
            print(f"[create_session] Résultat modification pause_collection=None: {sub_mod['status']}")

            time.sleep(2)  # Laisser le temps à Stripe d'appliquer la modification

            # Vérification après levée de la pause
            sub_after_pause = stripe.Subscription.retrieve(last_history.stripe_subscription_id)
            print(f"[create_session] Etat après suppression pause : pause_collection={sub_after_pause.get('pause_collection')}, status={sub_after_pause.get('status')}")

            # 2. Ensuite seulement : redémarrer le cycle de facturation
            sub_restart = stripe.Subscription.modify(
                last_history.stripe_subscription_id,
                cancel_at_period_end=False,
                billing_cycle_anchor="now",
                proration_behavior="none"
            )
            current_period_start = sub_restart.get('current_period_start')
            print(f"[create_session] Résultat redémarrage facturation: status={sub_restart['status']}, current_period_start={current_period_start}")
            
            return {"detail": "Subscription resumed successfully via existing Stripe subscription."}

        # 4. Sinon, créer une nouvelle session de paiement classique
        initial_bots_usage = 0
        if data.plan == "payg":
            stmt = select(func.count()).select_from(Bot).where(Bot.user_id == user_id)
            result = await db.execute(stmt)
            initial_bots_usage = result.scalar_one()
            print(f"[create_session] Initial bots usage for user {user_id}: {initial_bots_usage}")

        checkout_url = create_checkout_session(user_id, data.plan, initial_bots_usage)
        print(f"[create_session] Création session checkout URL: {checkout_url}")

        return {"url": checkout_url}

    except Exception as e:
        print(f"[create_session] Exception levée: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
        print(f"[Webhook] Événement Stripe reçu : {event['type']}")
    except stripe.error.SignatureVerificationError:
        print("[Webhook] Signature Stripe invalide.")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        print(f"[Webhook] Erreur lors de la construction de l'événement : {e}")
        raise HTTPException(status_code=400, detail="Webhook error")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        print(f"[Webhook] checkout.session.completed déclenché - Session ID: {session.get('id')}")

        try:
            user_id = UUID(session["metadata"]["user_id"])
            plan = session["metadata"]["plan"]
            new_stripe_subscription_id = session.get("subscription")
        except Exception as e:
            print(f"[Webhook] Erreur d'extraction des métadonnées : {e}")
            raise HTTPException(status_code=400, detail="Invalid session metadata")

        try:
            stripe_subscription = stripe.Subscription.retrieve(new_stripe_subscription_id)
        except Exception as e:
            print(f"[Webhook] Échec de la récupération de l'abonnement Stripe : {e}")
            raise HTTPException(status_code=500, detail="Stripe subscription retrieval error")

        item_messages_id = None
        item_bots_id = None
        for item in stripe_subscription['items']['data']:
            price_id = item['price']['id']
            if price_id == MESSAGE_PRICE_ID:
                item_messages_id = item['id']
            elif price_id == BOT_PRICE_ID:
                item_bots_id = item['id']

        stmt = select(Subscription).where(Subscription.user_id == user_id)
        result = await db.execute(stmt)
        subscription = result.scalars().first()

        if subscription and subscription.stripe_subscription_id != new_stripe_subscription_id:
            try:
                stripe.Subscription.delete(subscription.stripe_subscription_id)
            except Exception as e:
                print(f"[Webhook] Erreur annulation ancien abonnement : {e}")

        if not subscription:
            subscription = Subscription(user_id=user_id)
            db.add(subscription)

        subscription.plan = plan
        subscription.start_date = datetime.utcnow()
        subscription.status = SubscriptionStatus.active
        subscription.stripe_subscription_id = new_stripe_subscription_id
        subscription.stripe_subscription_item_messages = item_messages_id
        subscription.stripe_subscription_item_bots = item_bots_id

        try:
            await db.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database commit error")

        if plan == "payg" and item_bots_id:
            try:
                stmt = select(Bot).where(Bot.user_id == user_id)
                initial_bots_usage = await db.execute(stmt).count()
                report_usage(subscription_item_id=item_bots_id, quantity=initial_bots_usage, increment=False)
            except Exception as e:
                print(f"[Webhook] Erreur usage initial : {e}")

    elif event["type"] == "invoice.paid":
        invoice = event["data"]["object"]
        stripe_subscription_id = invoice["subscription"]
        stmt = select(Subscription).where(Subscription.stripe_subscription_id == stripe_subscription_id)
        result = await db.execute(stmt)
        subscription = result.scalars().first()
        if subscription:
            subscription.status = SubscriptionStatus.active
            await db.commit()

    elif event["type"] == "invoice.payment_failed":
        invoice = event["data"]["object"]
        stripe_subscription_id = invoice["subscription"]
        stmt = select(Subscription).where(Subscription.stripe_subscription_id == stripe_subscription_id)
        result = await db.execute(stmt)
        subscription = result.scalars().first()
        if subscription:
            subscription.status = SubscriptionStatus.unpaid
            print("fonction qui notifie l'utilisateur de l'échec du paiement")
            await db.commit()

    elif event["type"] == "customer.subscription.deleted":
        subscription_data = event["data"]["object"]
        stripe_subscription_id = subscription_data["id"]
        stmt = select(Subscription).where(Subscription.stripe_subscription_id == stripe_subscription_id)
        result = await db.execute(stmt)
        subscription = result.scalars().first()
        if subscription:
            subscription.status = SubscriptionStatus.cancelled
            await db.commit()

    elif event["type"] == "customer.subscription.updated":
        subscription_data = event["data"]["object"]
        stripe_subscription_id = subscription_data["id"]
        new_status = subscription_data["status"]

        # Vérifie si abonnement est en pause via pause_collection venant de Stripe
        pause_collection = subscription_data.get("pause_collection")
        if pause_collection and pause_collection.get("behavior") == "mark_uncollectible":
            new_status = "paused"

        # Récupération en base
        stmt = select(Subscription).where(Subscription.stripe_subscription_id == stripe_subscription_id)
        result = await db.execute(stmt)
        subscription = result.scalars().first()
        if not subscription:
            return {"status": "not_found"}

        # Mettre à jour le statut (try/except si statut inconnu)
        try:
            subscription.status = SubscriptionStatus(new_status)
        except ValueError:
            subscription.status = SubscriptionStatus.unpaid

        # Si pause => basculer en free et réinitialiser certains champs
        if new_status == "paused":
            subscription.plan = PlanEnum.FREE
            subscription.stripe_subscription_id = None
            subscription.stripe_subscription_item_bots = None
            subscription.stripe_subscription_item_messages = None
            subscription.message_limit = None
            subscription.start_date = datetime.utcnow()

        else:
            try:
                price_ids = [item["price"]["id"] for item in subscription_data["items"]["data"]]

                if PREMIUM_PRICE_ID in price_ids:
                    if subscription.plan != PlanEnum.PREMIUM:
                        subscription.start_date = datetime.utcnow()
                    subscription.plan = PlanEnum.PREMIUM

                elif any(pid in price_ids for pid in [MESSAGE_PRICE_ID, BOT_PRICE_ID]):
                    if subscription.plan != PlanEnum.PAYG:
                        subscription.start_date = datetime.utcnow()
                    subscription.plan = PlanEnum.PAYG
                    subscription.message_count = 0
                else:
                    subscription.plan = PlanEnum.FREE

                subscription.last_reset = datetime.utcnow().date()
            except Exception as e:
                print(f"[Webhook] Erreur mise à jour plan : {e}")

        # Enregistre l'historique
        history = SubscriptionHistory(
            subscription_id=subscription.id,
            user_id=subscription.user_id,
            plan=subscription.plan,
            start_date=subscription.start_date,
            message_count=subscription.message_count,
            free_message_count=subscription.free_message_count,
            last_reset=subscription.last_reset,
            status=subscription.status,
            message_limit=subscription.message_limit,
            stripe_subscription_id=subscription.stripe_subscription_id,
            stripe_subscription_item_messages=subscription.stripe_subscription_item_messages,
            stripe_subscription_item_bots=subscription.stripe_subscription_item_bots
        )
        db.add(history)
        await db.commit()

    return {"status": "success"}


@router.delete("/subscription")
async def cancel_subscription(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    user = await get_user_from_token(token, db, credentials_exception)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    stmt = select(Subscription).where(Subscription.user_id == user.id)
    result = await db.execute(stmt)
    subscription = result.scalars().first()

    if not subscription or not subscription.stripe_subscription_id:
        raise HTTPException(status_code=404, detail="Subscription not found")

    try:
        if subscription.plan == PlanEnum.PAYG:
            stripe.Invoice.create(
                customer=subscription.stripe_customer_id,
                subscription=subscription.stripe_subscription_id,
                auto_advance=True  # pour que la facture passe automatiquement en "open"
            )

        
        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=False,
            pause_collection={"behavior": "mark_uncollectible"}
        )

        # ✅ Optionnel : met à jour le statut dans ta base locale
        subscription.status = "paused"
        await db.commit()

        return {"detail": "Subscription has been paused immediately."}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))