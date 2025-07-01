import asyncio
import json
import logging
from functools import partial

from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from pywebpush import webpush, WebPushException

from app.database import SessionLocal
from app.db.models.models import FutureAction, Message, Conversation, PushSubscription
from app.utils.websocket_registry import get_active_websockets, unregister_websocket
from app.config import VAPID_PRIVATE_KEY

lock = asyncio.Lock()

VAPID_CLAIMS = {
    "sub": "mailto:contact@chathera.com"
}

def check_condition(condition: dict, db: Session, conversation: Conversation) -> bool:
    if condition.get("type") == "no_reply":
        hours = condition.get("timeout_hours", 24)
        since = datetime.now(timezone.utc) - timedelta(hours=hours)

        last_reply = db.query(Message).filter(
            Message.conversation_id == conversation.id,
            Message.user_id == conversation.user_id,
            Message.created_at >= since
        ).first()

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


async def send_notification_to_user(user_id: int, message: str, db: Session):
    subscriptions = db.query(PushSubscription).filter(PushSubscription.user_id == user_id).all()
    
    for sub in subscriptions:
        subscription_info = {
            "endpoint": sub.endpoint,
            "keys": sub.keys
        }
        try:
            await send_push(subscription_info, message)
            logging.info(f"Notification push envoyée à l'utilisateur {user_id}")
        except WebPushException as ex:
            logging.error(f"Erreur WebPush: {repr(ex)}")
            # Supprimer l'abonnement si il est expiré (statut HTTP 410 Gone)
            if ex.response and ex.response.status_code == 410:
                logging.info(f"Suppression abonnement push expiré pour user {user_id}, endpoint {sub.endpoint}")
                db.delete(sub)
                db.commit()


async def task_scheduler():
    """
    Tâche asynchrone qui tourne en boucle, vérifie les actions futures,
    et envoie soit via WebSocket si connecté, soit crée un message non lu + notifie.
    """
    while True:
        async with lock:
            db: Session = SessionLocal()
            try:
                now = datetime.now(timezone.utc)
                actions = db.query(FutureAction).filter(FutureAction.date_action <= now).all()

                for action in actions:
                    conversation = db.query(Conversation).filter_by(id=action.conversation_id).first()
                    if not conversation:
                        db.delete(action)
                        db.commit()
                        continue

                    if action.condition and not check_condition(action.condition, db, conversation):
                        continue

                    active_websockets = get_active_websockets()
                    websocket = active_websockets.get(conversation.user_id)

                    if websocket:
                        print(f"Tentative d'envoi WebSocket pour {conversation.user_id} avec message : {action.future_message}")
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

                        # Envoi notification push
                        #await send_notification_to_user(conversation.user_id, action.future_message, db)

                    db.delete(action)
                    db.commit()
            finally:
                db.close()

        await asyncio.sleep(2.5)  # Pause 5 secondes avant prochaine vérification
