import asyncio

from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.db.models.models import FutureAction, Message, Conversation
from app.utils.websocket_registry import get_active_websockets


async def task_scheduler():
    while True:
        async with asyncio.Lock():
            db: Session = SessionLocal()
            now = datetime.now(timezone.utc)

            actions = db.query(FutureAction).filter(FutureAction.date_action <= now).all()
            for action in actions:
                conv = db.query(Conversation).filter_by(id=action.conversation_id).first()
                if not conv:
                    continue

                # Vérifier conditions optionnelles
                if action.condition:
                    if not check_condition(action.condition, db, conv):
                        continue

                websocket = get_active_websockets().get(conv.user_id)
                reply_msg = Message(
                    user_id=conv.bot_id,
                    content=action.future_message,
                    conversation_id=conv.id,
                    timestamp=now
                )
                db.add(reply_msg)
                db.delete(action)

                db.commit()

                # Si connecté : envoie via WebSocket
                if websocket:
                    await websocket.send_json({
                        "type": "future_action",
                        "message": action.future_message,
                        "timestamp": now.isoformat()
                    })
            db.close()
        await asyncio.sleep(5)


def check_condition(condition: dict, db: Session, conversation: Conversation) -> bool:
    if condition.get("type") == "no_reply":
        hours = condition.get("timeout_hours", 24)
        since = datetime.utcnow() - timedelta(hours=hours)

        last_reply = db.query(Message).filter(
            Message.conversation_id == conversation.id,
            Message.user_id == conversation.user_id,
            Message.created_at >= since
        ).first()

        return last_reply is None
    return True
