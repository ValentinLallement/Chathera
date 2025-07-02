import stripe
import os

from uuid import UUID
from datetime import datetime
from sqlmodel import Session

from app.config import STRIPE_SECRET_KEY,PREMIUM_PRICE_ID,PAYG_PRICE_ID,BOT_PRICE_ID
from app.db.models.models import Subscription, SubscriptionHistory

stripe.api_key = STRIPE_SECRET_KEY

def create_checkout_session(user_id: UUID, plan: str, initial_bots_usage: int = 0) -> str:
    """
    Crée une session Stripe pour l'utilisateur avec un plan donné.
    Pour le plan PAYG, on initialise les compteurs d'usage avec les quantités déjà consommées.
    """

    if plan == "premium":
        line_items = [
            {
                "price": PREMIUM_PRICE_ID,
                "quantity": 1,
            }
        ]
    elif plan == "payg":
        line_items = [
            {
                "price": PAYG_PRICE_ID,
                "quantity": 1,
            }
        ]
        print(line_items)
    else:
        raise ValueError(f"Plan inconnu : {plan}")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=line_items,
        mode="subscription",
        metadata={
            "user_id": str(user_id),
            "plan": plan,
        },
        success_url="http://localhost:5173/success",
        cancel_url="http://localhost:5173/cancel",
    )

    return session.url

def cancel_stripe_subscription(stripe_subscription_id: str):
    stripe.Subscription.delete(stripe_subscription_id)

    
def log_subscription_history(db: Session, subscription: Subscription):
    history = SubscriptionHistory(
        subscription_id=subscription.id,
        user_id=subscription.user_id,
        plan=subscription.plan,
        start_date=subscription.start_date,
        message_count=subscription.message_count,
        last_reset=subscription.last_reset,
        status=subscription.status,
        message_limit=subscription.message_limit,
        stripe_subscription_id=subscription.stripe_subscription_id,
        stripe_subscription_item_messages=subscription.stripe_subscription_item_messages,
        stripe_subscription_item_bots=subscription.stripe_subscription_item_bots,
        recorded_at=datetime.utcnow()
    )
    db.add(history)
    db.commit()