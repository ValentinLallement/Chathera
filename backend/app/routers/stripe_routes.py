import stripe

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
from app.db.models.models import Subscription,SubscriptionStatus,Bot
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
    user_id = user.id if user else None

    try:
        initial_bots_usage = 0
        if data.plan == "payg":
            stmt = select(func.count()).select_from(Bot).where(Bot.user_id == user_id)
            result = await db.execute(stmt)
            initial_bots_usage = result.scalar_one()  # récupère le count directement
            print(f"Initial bots usage for user {user_id}: {initial_bots_usage}")

        checkout_url = create_checkout_session(user_id, data.plan, initial_bots_usage)
        return {"url": checkout_url}

    except Exception as e:
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

        stmt = select(Subscription).where(Subscription.stripe_subscription_id == stripe_subscription_id)
        result = await db.execute(stmt)
        subscription = result.scalars().first()
        if not subscription:
            return {"status": "not_found"}

        try:
            subscription.status = SubscriptionStatus(new_status)
        except ValueError:
            subscription.status = SubscriptionStatus.unpaid

        try:
            price_ids = [item["price"]["id"] for item in subscription_data["items"]["data"]]
            if MESSAGE_PRICE_ID in price_ids:
                subscription.plan = "messages"
            elif BOT_PRICE_ID in price_ids:
                subscription.plan = "bots"
            else:
                subscription.plan = "custom"
        except Exception as e:
            print(f"[Webhook] Erreur mise à jour plan : {e}")

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
        cancel_stripe_subscription(subscription.stripe_subscription_id)

        subscription.status = "cancelled"
        await db.commit()
        return {"detail": "Subscription cancelled successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))