from datetime import datetime
from app.models import PlanEnum, Subscription

BOT_LIMITS = {
    PlanEnum.FREE: 1,
    PlanEnum.PREMIUM: 1,
}

MESSAGE_LIMITS = {
    PlanEnum.FREE: 10,
    PlanEnum.PREMIUM: 600,
}


def check_bot_limit(subscription: Subscription, current_bot_count: int) -> bool:
    limit = BOT_LIMITS[subscription.plan]
    return current_bot_count < limit


def check_message_limit(subscription: Subscription) -> bool:
    today = datetime.utcnow().date()

    # ----- PAYG et PREMIUM → Reset mensuel -----
    if subscription.plan in [PlanEnum.PREMIUM, PlanEnum.PAYG]:
        if subscription.last_reset < today.replace(day=1):
            subscription.message_count = 0
            subscription.last_reset = today

    # ----- FREE : limite à vie (pas de reset) -----
    if subscription.plan == PlanEnum.FREE:
        return subscription.message_count < MESSAGE_LIMITS[PlanEnum.FREE]

    # ----- PREMIUM -----
    if subscription.plan == PlanEnum.PREMIUM:
        return subscription.message_count < MESSAGE_LIMITS[PlanEnum.PREMIUM]

    # ----- PAYG -----
    if subscription.plan == PlanEnum.PAYG:
        if subscription.message_limit is None:
            return True  # pas de limite définie
        return subscription.message_count < subscription.message_limit

    return False  # fallback sécurité

def increment_message_count(subscription: Subscription):
    today = datetime.utcnow().date()
    if subscription.last_reset < today.replace(day=1):
        subscription.message_count = 0
        subscription.last_reset = today

    subscription.message_count += 1
