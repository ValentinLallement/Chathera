import asyncio
import json
from functools import partial

from datetime import datetime, timezone, timedelta
from sqlmodel import Session
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from pywebpush import webpush, WebPushException

from app.database import async_session
from app.db.models.models import FutureAction, Message, Conversation, PushSubscription
from app.utils.websocket_registry import get_active_websockets, unregister_websocket
from app.config import VAPID_PRIVATE_KEY

lock = asyncio.Lock()

VAPID_CLAIMS = {
    "sub": "mailto:contact@chathera.com"
}

async def check_condition(condition: dict, db: AsyncSession, conversation: Conversation) -> bool:
    if condition.get("type") == "no_reply":
        hours = condition.get("timeout_hours", 24)
        since = datetime.utcnow() - timedelta(hours=hours)

        stmt = select(Message).where(
            Message.conversation_id == conversation.id,
            Message.user_id == conversation.user_id,
            Message.created_at >= since
        )
        result = await db.execute(stmt)
        last_reply = result.scalars().first()

        return last_reply is None
    return True


async def send_push(subscription_info: dict, message: str):
    """
    Envoie la notification push en mode thread-safe (non bloquant l'event loop asyncio)
    """
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        partial(
            webpush,
            subscription_info,
            data=json.dumps({"message": message}),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS
        )
    )


async def send_notification_to_user(user_id: int, message: str, db: AsyncSession):
    stmt = select(PushSubscription).where(PushSubscription.user_id == user_id)
    result = await db.execute(stmt)
    subscriptions = result.scalars().all()

    for sub in subscriptions:
        subscription_info = {
            "endpoint": sub.endpoint,
            "keys": sub.keys
        }
        try:
            await send_push(subscription_info, message)
            print(f"Notification push envoyée à l'utilisateur {user_id}")
        except WebPushException as ex:
            print(f"Erreur WebPush: {repr(ex)}")
            if ex.response and ex.response.status_code == 410:
                print(f"Suppression abonnement push expiré pour user {user_id}, endpoint {sub.endpoint}")
                await db.delete(sub)
                await db.commit()


async def task_scheduler():
    while True:
        async with lock:
            async with async_session() as db:
                try:
                    now = datetime.utcnow().replace(tzinfo=None)
                    stmt_actions = select(FutureAction).where(FutureAction.date_action <= now)
                    result_actions = await db.execute(stmt_actions)
                    actions = result_actions.scalars().all()

                    for action in actions:
                        stmt_conv = select(Conversation).where(Conversation.id == action.conversation_id)
                        result_conv = await db.execute(stmt_conv)
                        conversation = result_conv.scalars().first()

                        if not conversation:
                            await db.delete(action)
                            await db.commit()
                            continue

                        if action.condition and not await check_condition(action.condition, db, conversation):
                            continue

                        active_websockets = get_active_websockets()
                        websocket = active_websockets.get(conversation.user_id)

                        if websocket:
                            try:
                                await websocket.send_json({
                                    "type": "future_action",
                                    "message": action.future_message,
                                    "timestamp": now.isoformat()
                                })
                                msg = Message(
                                    user_id=conversation.bot_id,
                                    content=action.future_message,
                                    conversation_id=conversation.id,
                                    timestamp=now,
                                    read=True
                                )
                                db.add(msg)
                                await db.commit()
                            except Exception as e:
                                print(f"Erreur envoi WebSocket future_action pour user {conversation.user_id} : {e}")
                                unregister_websocket(conversation.user_id)
                                websocket = None

                        if not websocket:
                            future_msg = Message(
                                user_id=conversation.bot_id,
                                content=action.future_message,
                                conversation_id=conversation.id,
                                timestamp=now,
                                read=False
                            )
                            db.add(future_msg)
                            await db.commit()

                            

                        await db.delete(action)
                        await db.commit()

                except Exception as e:
                    print(f"Erreur dans task_scheduler: {e}")
                    

        await asyncio.sleep(2.5)
