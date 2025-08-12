import stripe
import time

from uuid import UUID
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request
from fastapi import Depends,status
from fastapi.security import OAuth2PasswordBearer

from stripe import billing_portal

from sqlmodel import Session, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import func

from app.utils.stripe import create_checkout_session,cancel_stripe_subscription
from app.config import STRIPE_WEBHOOK_SECRET,PREMIUM_PRICE_ID,PAYG_PRICE_ID
from app.schemas import CheckoutRequest
from app.dependencies import get_db
from app.auth import get_user_from_token
from app.crud import update_user_subscription
from app.db.models.models import Subscription,SubscriptionStatus,Bot, PlanEnum, SubscriptionHistory, User
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

        # 0. Vérifier si l'utilisateur a une subscription en impayé
        stmt = select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.status == SubscriptionStatus.unpaid
        )
        result = await db.execute(stmt)
        unpaid_subscription = result.scalars().first()
        if unpaid_subscription:
            if not user.stripe_customer_id:
                raise HTTPException(status_code=403, detail="You have unpaid invoices. Please contact support.")
            portal_session = stripe.billing_portal.Session.create(
                customer=user.stripe_customer_id,
                return_url="https://chathera.com/dashboard"
            )
            raise HTTPException(
                status_code=403, 
                detail=f"You have unpaid invoices. Please regularize your payment here: {portal_session.url}"
            )

        # 1. Vérifier si abonnement actif du même type → bloquer
        stmt = select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.plan == data.plan,
            Subscription.status == SubscriptionStatus.active
        )
        result = await db.execute(stmt)
        same_plan_subscription = result.scalars().first()
        if same_plan_subscription:
            print(f"[create_session] Abonnement du même type déjà actif: {same_plan_subscription.id}")
            raise HTTPException(status_code=400, detail="You already have an active subscription of this type.")    

        # 2. Compter les bots si PAYG
        initial_bots_usage = 0
        if data.plan == "payg":
            stmt = select(func.count()).select_from(Bot).where(Bot.user_id == user_id)
            result = await db.execute(stmt)
            initial_bots_usage = result.scalar_one()
            print(f"[create_session] Initial bots usage for user {user_id}: {initial_bots_usage}")

        # 4. Créer session checkout
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
            initial_bots_usage = int(session["metadata"].get("initial_bots_usage", "0"))  # Ajouté ici
        except Exception as e:
            print(f"[Webhook] Erreur d'extraction des métadonnées : {e}")
            raise HTTPException(status_code=400, detail="Invalid session metadata")

        try:
            stripe_subscription = stripe.Subscription.retrieve(new_stripe_subscription_id)
        except Exception as e:
            print(f"[Webhook] Échec de la récupération de l'abonnement Stripe : {e}")
            raise HTTPException(status_code=500, detail="Stripe subscription retrieval error")

        # Récupère et enregistre le customer_id dans l'utilisateur s'il ne l'a pas encore
        customer_id = stripe_subscription.get("customer")

        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalars().first()

        if user and not user.stripe_customer_id:
            user.stripe_customer_id = customer_id
            db.add(user)
            await db.commit()
            print(f"[Webhook] stripe_customer_id enregistré pour user {user_id}: {customer_id}")

        # Récupère les IDs d'items
        item_messages_id = None
        item_bots_id = None
        for item in stripe_subscription['items']['data']:
            price_id = item['price']['id']
            if price_id == MESSAGE_PRICE_ID:
                item_messages_id = item['id']
            elif price_id == BOT_PRICE_ID:
                item_bots_id = item['id']

        # Supprimer l'ancien abonnement s'il existe et est différent
        stmt = select(Subscription).where(Subscription.user_id == user_id)
        result = await db.execute(stmt)
        subscription = result.scalars().first()

        if subscription:
            old_stripe_subscription_id = subscription.stripe_subscription_id
            if old_stripe_subscription_id and old_stripe_subscription_id != new_stripe_subscription_id:
                try:
                    print(f"[Webhook] Ancien abonnement trouvé, suppression de l'abonnement Stripe ID: {old_stripe_subscription_id}")
                    stripe.Subscription.delete(old_stripe_subscription_id)
                except Exception as e:
                    print(f"[Webhook] Erreur annulation ancien abonnement : {e}")
            else:
                print("[Webhook] Aucun ancien abonnement à annuler ou abonnement identique.")
        else:
            print("[Webhook] Aucun abonnement existant trouvé pour cet utilisateur.")
            subscription = Subscription(user_id=user_id)
            db.add(subscription)

        subscription.plan = plan
        subscription.start_date = datetime.now(timezone.utc)
        subscription.status = SubscriptionStatus.active
        subscription.stripe_subscription_id = new_stripe_subscription_id
        subscription.stripe_subscription_item_messages = item_messages_id
        subscription.stripe_subscription_item_bots = item_bots_id

        try:
            await db.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database commit error")
        print(subscription)
        # Enregistrement de l'usage initial des bots
        if plan == "payg" and item_bots_id and initial_bots_usage > 0:
            try:
                stripe.SubscriptionItem.create_usage_record(
                    subscription_item=item_bots_id,
                    quantity=initial_bots_usage,
                    timestamp=int(time.time()),  # maintenant
                    action="set"  # écrase le compteur initial
                )
                print(f"[Webhook] Usage initial de {initial_bots_usage} bots enregistré pour item {item_bots_id}")
            except Exception as e:
                print(f"[Webhook] Erreur enregistrement usage initial : {e}")

    elif event["type"] == "invoice.paid":
        invoice = event["data"]["object"]
    
        stripe_subscription_id = invoice.get("subscription")
        if not stripe_subscription_id:
            parent = invoice.get("parent", {})
            subscription_details = parent.get("subscription_details", {}) if parent else {}
            stripe_subscription_id = subscription_details.get("subscription")
    
        if not stripe_subscription_id:
            # On peut essayer dans les lignes, ou ignorer
            print("[Webhook] invoice.paid reçu sans subscription, on ignore")
            return {"status": "ignored"}

    elif event["type"] == "invoice.payment_failed":
        invoice = event["data"]["object"]
        stripe_subscription_id = invoice.get("subscription")
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

        # Recherche de l'abonnement dans la base par stripe_subscription_id
        stmt = select(Subscription).where(Subscription.stripe_subscription_id == stripe_subscription_id)
        result = await db.execute(stmt)
        subscription = result.scalars().first()

        if subscription:
            # Met à jour le statut en cancelled
            subscription.status = SubscriptionStatus.canceled

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
            # Réinitialisation des champs
            subscription.plan = PlanEnum.FREE
            subscription.stripe_subscription_id = None
            subscription.stripe_subscription_item_bots = None
            subscription.stripe_subscription_item_messages = None
            subscription.message_limit = None
            subscription.start_date = None
            subscription.status = SubscriptionStatus.active


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
            subscription.start_date = datetime.now(timezone.utc)

        else:
            try:
                price_ids = [item["price"]["id"] for item in subscription_data["items"]["data"]]

                if PREMIUM_PRICE_ID in price_ids:
                    if subscription.plan != PlanEnum.PREMIUM:
                        subscription.start_date = datetime.now(timezone.utc)
                    subscription.plan = PlanEnum.PREMIUM

                elif any(pid in price_ids for pid in [MESSAGE_PRICE_ID, BOT_PRICE_ID]):
                    if subscription.plan != PlanEnum.PAYG:
                        subscription.start_date = datetime.now(timezone.utc)
                    subscription.plan = PlanEnum.PAYG
                    subscription.message_count = 0
                else:
                    subscription.plan = PlanEnum.FREE

                subscription.last_reset = datetime.now(timezone.utc).date()
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

    # Récupérer l'abonnement actif de l'utilisateur
    stmt = select(Subscription).where(
        Subscription.user_id == user.id,
        Subscription.status == SubscriptionStatus.active  # ou adapte selon ton modèle
    )
    result = await db.execute(stmt)
    subscription = result.scalars().first()

    if not subscription or not subscription.stripe_subscription_id:
        raise HTTPException(status_code=404, detail="Subscription not found")

    try:
        # Pour le modèle PAYG, créer une facture finale pour l'usage
        if subscription.plan == PlanEnum.PAYG and user.stripe_customer_id:
            stripe.Invoice.create(
                customer=user.stripe_customer_id,
                subscription=subscription.stripe_subscription_id,
                auto_advance=True 
            )

        # Annulation immédiate sur Stripe (supprime la souscription)
        stripe.Subscription.delete(subscription.stripe_subscription_id)

        return {"detail": "Subscription cancelled immediately."}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")

@router.post("/customer-portal")
async def create_customer_portal(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    user = await get_user_from_token(token, db, credentials_exception)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    # 🔍 Cherche l'abonnement actif lié à l'utilisateur
    stmt = select(Subscription).where(
        Subscription.user_id == user.id,
        Subscription.status == SubscriptionStatus.active
    )
    result = await db.execute(stmt)
    subscription = result.scalars().first()

    if not subscription or not user.stripe_customer_id :
        raise HTTPException(status_code=404, detail="Aucun abonnement actif ou Stripe ID manquant")

    try:
        session = stripe.billing_portal.Session.create(
            customer=user.stripe_customer_id,
            return_url="https://chathera.com/dashboard"
        )
        return {"url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur Stripe: {str(e)}")
