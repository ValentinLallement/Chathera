import stripe
import os

from uuid import UUID

from app.config import STRIPE_SECRET_KEY,PREMIUM_PRICE_ID,PAYG_PRICE_ID,BOT_PRICE_ID

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
        success_url="https://ton-frontend/success",
        cancel_url="https://ton-frontend/cancel",
    )

    return session.url

def cancel_stripe_subscription(stripe_subscription_id: str):
    stripe.Subscription.delete(stripe_subscription_id)

    