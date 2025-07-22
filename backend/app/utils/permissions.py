from datetime import datetime
from sqlmodel import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.models import PlanEnum, Subscription

BOT_LIMITS = {
    PlanEnum.FREE: 1,
    PlanEnum.PREMIUM: 2,
    PlanEnum.PAYG: None, 
}

MESSAGE_LIMITS = {
    PlanEnum.FREE: 10,
    PlanEnum.PREMIUM: 600,
    PlanEnum.PAYG: None,  
}


async def check_bot_limit(subscription: Subscription, current_bot_count: int) -> bool:
    limit = BOT_LIMITS.get(subscription.plan)
    print(f"[check_bot_limit] Plan: {subscription.plan}, Limit: {limit}, Current Count: {current_bot_count}")
    if subscription.status != "active":
        return False
    if limit is None:
        return True  # illimité
    return current_bot_count < limit


async def check_message_limit(subscription: Subscription, db: AsyncSession) -> bool:
    today = datetime.utcnow().date()

    if subscription.status != "active":
        return False
    
    # Réinitialisation mensuelle (sauf pour FREE)
    if subscription.plan in [PlanEnum.PREMIUM, PlanEnum.PAYG]:
        if subscription.last_reset < today.replace(day=1):
            subscription.message_count = 0
            subscription.last_reset = today
            db.add(subscription)
            await db.commit()

    # Limite personnalisée pour PAYG (ex: override DB)
    if subscription.plan == PlanEnum.PAYG:
        if subscription.message_limit is not None:
            return subscription.message_count < subscription.message_limit
        return True 
    
    if subscription.plan == PlanEnum.FREE:
        if subscription.free_message_count >= 10 :
            return False

    if subscription.plan == PlanEnum.PREMIUM:
        if subscription.message_count >= 600:
            return False

    return True

def increment_message_count(subscription: Subscription):
    today = datetime.utcnow().date()
    if subscription.last_reset < today.replace(day=1):
        subscription.message_count = 0
        subscription.last_reset = today

    subscription.message_count += 1
