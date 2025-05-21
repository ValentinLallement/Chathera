import uuid
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect,Depends
from uuid import uuid4
from app.models import Message, Conversation, Memory, FutureAction, MemoryType, MemoryImportance, MemoryEntry
from app.database import get_session
from app.dependencies import get_user_from_websocket, get_db
from datetime import datetime,timedelta
from app.utils.auto_reply import build_prompt, get_auto_reply_from_deepseek,search_memory
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
        # Exemple de tâche en arrière-plan pour les actions futures (désactivée ici)
        # asyncio.create_task(check_and_send_future_actions(user, db, websocket))

        while True:
            # Réception du message envoyé par le client
            try:
                data = await websocket.receive_text()
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Erreur lors de la réception du message : {str(e)}",
                    "timestamp": datetime.utcnow().isoformat()
                })
                continue

            # Tentative de décoder le JSON reçu
            try:
                message_data = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Format JSON invalide",
                    "timestamp": datetime.utcnow().isoformat()
                })
                continue

            # Vérification de la présence du bot_id dans le message
            bot_id_str = message_data.get("bot_id")
            if not bot_id_str:
                await websocket.send_json({
                    "type": "error",
                    "message": "Erreur: bot_id manquant",
                    "timestamp": datetime.utcnow().isoformat()
                })
                continue

            # Conversion du bot_id en UUID
            try:
                bot_id = uuid.UUID(bot_id_str)
            except ValueError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Erreur: bot_id invalide",
                    "timestamp": datetime.utcnow().isoformat()
                })
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
                content=message_data.get("content", ""),
                conversation_id=conversation.id,
                timestamp=timestamp
            )
            db.add(message)
            db.commit()

            # Recherche de souvenirs pertinents à partir du message
            souvenirs = search_memory(
                user_message=message.content,
                user_id=str(conversation.id),
                type_filter=[MemoryType.LONG, MemoryType.BEHAVIOR],
                importance_filter=[MemoryImportance.HIGH, MemoryImportance.CRITICAL]
            )
            souvenirs_pertinents = souvenirs[:5]  # limite manuelle

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

            # Dernier message utilisateur pour structurer le prompt
            dernier_message = {
                "auteur": user.name,
                "contenu": message.content,
                "date": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "user_id": str(user.id),
                "conversation_id": str(conversation.id)
            }

            # Récupération des événements à venir dans les 7 prochains jours
            now = datetime.utcnow()
            soon = now + timedelta(days=7)
            events_soon = db.query(MemoryEntry).filter(
                MemoryEntry.type == MemoryType.EVENT,
                MemoryEntry.event_date != None,
                MemoryEntry.event_date >= now,
                MemoryEntry.event_date <= soon
            ).all()

            event_summary = (
                "\n".join(f"- ({e.event_date.strftime('%Y-%m-%d')}) {e.content}" for e in events_soon)
                if events_soon else
                "Aucun événement à venir."
            )

            # Récupérations des directives triées par importance et date
            directives_entries = db.query(MemoryEntry).filter(
                MemoryEntry.conversation_id == conversation.id,
                MemoryEntry.type == MemoryType.DIRECTIVE
            ).order_by(MemoryEntry.importance.desc(), MemoryEntry.created_at.desc()).all()

            directives = [d.content for d in directives_entries]
            directives_text = "\n".join(f"- {d}" for d in directives) if directives else "Aucune directive spécifique."

            # Récupérations des informations personnelles
            personal_entries = [m.content for m in memories if m.type == MemoryType.PERSONAL]
            personal_information = (
                "\n".join(f"- {entry}" for entry in personal_entries)
                if personal_entries else
                "Aucune information personnelle disponible."
            )

            # Construction du prompt à envoyer à Grok
            prompt = build_prompt(
                messages_recents,
                dernier_message,
                souvenirs_pertinents,
                directives_text,
                personal_information,
                event_summary
            )
            print(f"Prompt envoyé à Grok : {prompt}")
            # Appel à la fonction de génération de réponse automatique Grok
            auto_reply = get_auto_reply_from_deepseek(prompt, conversation.id, db)

            # Vérification des erreurs dans la réponse de Grok
            if "error" in auto_reply:
                await websocket.send_json({
                    "type": "error",
                    "message": auto_reply["error"],
                    "timestamp": datetime.utcnow().isoformat()
                })
                continue

            # Enregistrement des actions futures retournées par Grok
            for action_data in auto_reply.get("actions", []):
                try:
                    date_action = datetime.fromisoformat(action_data.get("date", ""))
                except (ValueError, TypeError):
                    date_action = datetime.utcnow()

                future_action = FutureAction(
                    conversation_id=conversation.id,
                    action=action_data.get("type", ""),
                    date_action=date_action,
                    future_message=action_data.get("message", "")
                )
                db.add(future_action)
            db.commit()

            # Envoi immédiat du premier message d'action si existant
            reply_message = auto_reply.get("actions", [{}])[0].get("message", "Désolé, une erreur est survenue.")
            reply_msg = Message(
                user_id=bot_id,
                content=reply_message,
                conversation_id=conversation.id,
                timestamp=timestamp
            )
            db.add(reply_msg)
            db.commit()

            # Envoi de la réponse du bot au client WebSocket
            await websocket.send_json({
                "type": "reponse",
                "message": reply_message,
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

"""
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
"""