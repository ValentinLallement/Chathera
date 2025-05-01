import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect,Depends
from uuid import uuid4
from app.models import Message, Conversation, Memory, FutureAction
from app.database import get_session
from app.dependencies import get_user_from_websocket, get_db
from datetime import datetime
from app.utils.auto_reply import build_prompt, get_auto_reply_from_grok
import json
from sqlalchemy.orm import Session


websocket_router = APIRouter()

session = get_session()  # Ne pas oublier d'utiliser la session dans le bon contexte

@websocket_router.websocket("/ws/chat")
async def chat(websocket: WebSocket, db: Session = Depends(get_db)):
    # Récupération de l'utilisateur à partir du WebSocket
    user = await get_user_from_websocket(websocket)  # Assumez que cette fonction est définie
    if not user:
        await websocket.close()
        return

    await websocket.accept()

    try:
        while True:
            # Réception du message envoyé par le client
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Vérification de la présence du bot_id dans le message
            bot_id_str = message_data.get("bot_id")
            if not bot_id_str:
                await websocket.send_text("Erreur: bot_id manquant")
                continue

            # Conversion du bot_id en UUID
            try:
                bot_id = uuid.UUID(bot_id_str)
            except ValueError:
                await websocket.send_text("Erreur: bot_id invalide")
                continue

            # Récupération ou création de la conversation entre l'utilisateur et le bot
            conversation = db.query(Conversation).filter_by(user_id=user.id, bot_id=bot_id).first()
            if not conversation:
                conversation = Conversation(user_id=user.id, bot_id=bot_id)
                db.add(conversation)
                db.commit()
                db.refresh(conversation)

            # Création du message utilisateur avec timestamp
            timestamp = datetime.utcnow()
            message = Message(
                user_id=user.id,
                content=message_data["content"],
                conversation_id=conversation.id,
                timestamp=timestamp
            )
            db.add(message)
            db.commit()

            # Récupération des 10 derniers messages de la conversation
            messages_db = (
                db.query(Message)
                .filter(Message.conversation_id == conversation.id)
                .order_by(Message.created_at.desc())
                .limit(10)
                .all()
            )

            messages_recents = [
                {
                    "auteur": user.name if msg.user_id == user.id else "IA",
                    "contenu": msg.content,
                    "date": msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
                }
                for msg in reversed(messages_db)
            ]

            # Récupération des mémoires associées à la conversation
            memories = db.query(Memory).filter(Memory.conversation_id == conversation.id).all()
            memoire_court_terme = [m for m in memories if m.type == "court_terme"]
            memoire_long_terme = [m for m in memories if m.type == "long_terme"]

            # Dernier message utilisateur pour structurer le prompt
            dernier_message = {
                "auteur": user.name,
                "contenu": message_data["content"],
                "date": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "user_id": str(user.id),
                "conversation_id": str(conversation.id)
            }

            # Construction du prompt à envoyer à Grok
            prompt = build_prompt(messages_recents, dernier_message, memoire_court_terme, memoire_long_terme)

            # Appel à l'API Grok pour obtenir la réponse automatique
            auto_reply = get_auto_reply_from_grok(prompt)

            # Enregistrement de la réponse du bot (IA) dans la base de données
            reply_msg = Message(
                user_id=bot_id,  # Le bot envoie la réponse
                content=auto_reply.get("message", "Désolé, une erreur est survenue."),
                conversation_id=conversation.id,
                timestamp=datetime.utcnow()
            )
            db.add(reply_msg)

            # Mise à jour de la mémoire (si présente)
            for mem in auto_reply.get("nouvelle_memoire", []):
                db.add(Memory(
                    user_id=user.id,
                    conversation_id=conversation.id,
                    type=mem.get("type", "court_terme"),
                    contenu=mem.get("contenu", "")
                ))

            # Gestion des actions futures (si applicable)
            if auto_reply.get("future_action"):
                try:
                    date_action = datetime.fromisoformat(auto_reply.get("date_future_action"))
                except Exception:
                    date_action = datetime.utcnow()

                future = FutureAction(
                    conversation_id=conversation.id,
                    action=auto_reply["future_action"],
                    date_action=date_action,
                    future_message=auto_reply["future_message"]
                )
                db.add(future)

            db.commit()

            # Envoi de la réponse du bot au client WebSocket
            await websocket.send_json({
                "reply": auto_reply["message"],
                "timestamp": timestamp.isoformat()
            })

    except WebSocketDisconnect:
        print(f"Déconnexion utilisateur {user.id}")