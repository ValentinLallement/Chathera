from datetime import datetime, timezone
from sqlmodel import Session,select, asc
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.models import PlanEnum, Subscription,Bot

BOT_LIMITS = {
    PlanEnum.FREE: 1,
    PlanEnum.PREMIUM: 3,
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
    today = datetime.now(timezone.utc).date()

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

async def check_bot_access(
    db: AsyncSession,
    user_id: int,
    bot_id: int,
    plan: PlanEnum
) -> bool:
    """
    Vérifie si le bot_id fait partie des X premiers bots créés par l'utilisateur
    (X dépend du plan : 1 pour Free, 3 pour Premium, illimité pour Payg).
    Retourne True si l'accès est autorisé, sinon False.
    """
    if plan == PlanEnum.PAYG:
        return True  # accès illimité

    # Détermine la limite autorisée selon le plan
    if plan == PlanEnum.FREE:
        max_allowed = 1
    elif plan == PlanEnum.PREMIUM:
        max_allowed = 3
    else:
        max_allowed = 1  # fallback de sécurité

    # Récupère les X premiers bots créés par l'utilisateur
    result = await db.execute(
        select(Bot.id)
        .where(Bot.user_id == user_id)
        .order_by(asc(Bot.created_at))
        .limit(max_allowed)
    )
    allowed_bot_ids = [row[0] for row in result.fetchall()]

    # Retourne True si le bot fait partie des bots autorisés
    return bot_id in allowed_bot_ids