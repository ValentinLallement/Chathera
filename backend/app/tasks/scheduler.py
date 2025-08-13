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
        since = datetime.now(timezone.utc) - timedelta(hours=hours)

        stmt = select(Message).where(
            Message.conversation_id == conversation.id,
            Message.user_id == conversation.user_id,
            Message.created_at >= since
        )
        result = await db.execute(stmt)
        last_reply = result.scalars().first()

        return last_reply is None
    return True


async def task_scheduler():
    while True:
        try:
            async with async_session() as db:
                # Convert to timezone naive datetime for PostgreSQL storage
                now = datetime.now(timezone.utc).replace(tzinfo=None)

                # Get all pending actions
                actions = await db.execute(
                    select(FutureAction)
                    .where(FutureAction.date_action <= now)
                )
                actions = actions.scalars().all()

                for action in actions:
                    try:
                        conversation = await db.get(Conversation, action.conversation_id)
                        if not conversation:
                            continue

                        websocket = get_websocket(conversation.user_id)

                        if websocket:
                            try:
                                msg = Message(
                                    user_id=conversation.bot_id,
                                    content=action.future_message,
                                    conversation_id=conversation.id,
                                    created_at=datetime.now(timezone.utc).replace(tzinfo=None)  # Make timezone naive
                                )
                                db.add(msg)
                                await db.commit()

                                await websocket.send_json({
                                    "type": "reponse",
                                    "message": action.future_message,
                                    "timestamp": msg.created_at.isoformat()
                                })
                            except Exception as e:
                                print(f"Erreur envoi WebSocket future_action pour user {conversation.user_id} : {e}")
                                unregister_websocket(conversation.user_id)
                                websocket = None

                        if not websocket:
                            future_msg = Message(
                                user_id=conversation.bot_id,
                                content=action.future_message,
                                conversation_id=conversation.id,
                                created_at=now,  # Using the already naive datetime
                                read=False
                            )
                            db.add(future_msg)
                            await db.commit()

                        await db.delete(action)
                        await db.commit()
                    except Exception as e:
                        print(f"Error processing action {action.id}: {e}")
        except Exception as e:
                        print(f"Erreur dans task_scheduler: {e}")

        await asyncio.sleep(2.5)
