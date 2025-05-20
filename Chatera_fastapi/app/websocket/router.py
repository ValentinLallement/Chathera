import uuid
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect,Depends
from uuid import uuid4
from app.models import Message, Conversation, Memory, FutureAction
from app.database import get_session
from app.dependencies import get_user_from_websocket, get_db
from datetime import datetime
from app.utils.auto_reply import build_prompt, get_auto_reply_from_grok, get_auto_reply_from_deepseek
import json
from sqlalchemy.orm import Session


websocket_router = APIRouter()

session = get_session()  # Ne pas oublier d'utiliser la session dans le bon contexte

@websocket_router.websocket("/ws/chat")
async def chat(websocket: WebSocket, db: Session = Depends(get_db)):
    # Récupération de l'utilisateur à partir du WebSocket
    user = await get_user_from_websocket(websocket)
    if not user:
        await websocket.close()
        return

    await websocket.accept()

    try:
        # Démarrer la tâche en arrière-plan pour vérifier les actions futures
        asyncio.create_task(check_and_send_future_actions(user, db, websocket))

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
            conversation_id = conversation.id
            
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
            #auto_reply = get_auto_reply_from_grok(prompt)
            auto_reply = get_auto_reply_from_deepseek(prompt, conversation_id, db)
            

            # Vérification des erreurs dans la réponse de Grok
            if "error" in auto_reply:
                await websocket.send_json({
                    "type": "error",
                    "message": auto_reply["error"],
                    "timestamp": timestamp.isoformat()
                })
                continue

            # Enregistrement des réponses générées par Grok dans la base de données
            for action_data in auto_reply.get("actions", []):
                try:
                    # Vérification et extraction de la date de l'action (si présente)
                    date_action = datetime.fromisoformat(action_data.get("date", ""))
                except (ValueError, TypeError):
                    date_action = datetime.utcnow()  # Si la date est invalide, on utilise la date actuelle

                # Enregistrer l'action avec la date exacte dans FutureAction
                future_action = FutureAction(
                    conversation_id=conversation.id,
                    action=action_data.get("type", ""),  # Type d'action (répondre, etc.)
                    date_action=date_action,
                    future_message=action_data.get("message", "")  # Message de l'action future
                )
                db.add(future_action)

            db.commit()

            # Envoi immédiat si la date d'action est atteinte
            reply_message = auto_reply.get("actions", [{}])[0].get("message", "Désolé, une erreur est survenue.")
            reply_msg = Message(
                user_id=bot_id,
                content=reply_message,
                conversation_id=conversation.id,
                timestamp=timestamp
            )
            db.add(reply_msg)

            # Envoi de la réponse du bot au client WebSocket
            await websocket.send_json({
                "type": "message",
                "reply": reply_message,
                "timestamp": timestamp.isoformat()
            })

    except WebSocketDisconnect:
        print(f"Déconnexion utilisateur {user.id}")
    except Exception as e:
        print(f"Erreur inattendue : {str(e)}")
        await websocket.send_json({
            "type": "error",
            "message": f"Erreur inattendue : {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        })
        await websocket.close()


async def check_and_send_future_actions(user, db, websocket):
    # Fonction pour vérifier et envoyer les actions futures toutes les 5 secondes
    while True:
        now = datetime.utcnow()
        conversations = db.query(Conversation).filter(Conversation.user_id == user.id).all()
        
        for conversation in conversations:
            actions_to_send = db.query(FutureAction).filter(FutureAction.conversation_id == conversation.id).all()

            for future_action in actions_to_send:
                if future_action.date_action <= now:
                    # Envoi du message à la date précise
                    reply_msg = Message(
                        user_id=conversation.bot_id,
                        content=future_action.future_message,
                        conversation_id=conversation.id,
                        timestamp=now
                    )
                    db.add(reply_msg)
                    db.delete(future_action)  # Supprimer l'action après l'envoi

        db.commit()
        await asyncio.sleep(5)  # Attendre 5 secondes avant de vérifier à nouveau