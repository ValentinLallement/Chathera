from datetime import datetime
from app.db.models.models import PlanEnum, Subscription

BOT_LIMITS = {
    PlanEnum.FREE: 1,
    PlanEnum.PREMIUM: 1,
    PlanEnum.PAYG: None, 
}

MESSAGE_LIMITS = {
    PlanEnum.FREE: 10,
    PlanEnum.PREMIUM: 600,
    PlanEnum.PAYG: None,  
}


def check_bot_limit(subscription: Subscription, current_bot_count: int) -> bool:
    limit = BOT_LIMITS.get(subscription.plan)
    if limit is None:
        return True  # illimité
    return current_bot_count < limit


def check_message_limit(subscription: Subscription) -> bool:
    today = datetime.utcnow().date()

    # Réinitialisation mensuelle (sauf pour FREE)
    if subscription.plan in [PlanEnum.PREMIUM, PlanEnum.PAYG]:
        if subscription.last_reset < today.replace(day=1):
            subscription.message_count = 0
            subscription.last_reset = today

    # Limite personnalisée pour PAYG (ex: override DB)
    if subscription.plan == PlanEnum.PAYG:
        if subscription.message_limit is not None:
            return subscription.message_count < subscription.message_limit
        return True 

    # Récupère limite standard (FREE ou PREMIUM)
    limit = MESSAGE_LIMITS.get(subscription.plan)
    if limit is None:
        return True 

    return subscription.message_count < limit

def increment_message_count(subscription: Subscription):
    today = datetime.utcnow().date()
    if subscription.last_reset < today.replace(day=1):
        subscription.message_count = 0
        subscription.last_reset = today

    subscription.message_count += 1
