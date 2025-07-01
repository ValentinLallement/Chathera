import uuid
import asyncio
import re
import json
import traceback
from typing import List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect,Depends
from sqlalchemy.orm import Session

from uuid import uuid4, UUID
from datetime import datetime,timedelta

from app.db.models.models import Message, Conversation, FutureAction, MemoryType, MemoryImportance, MemoryEntry, Subscription
from app.database import get_session
from app.dependencies import get_user_from_websocket,get_db
from app.utils.auto_reply import build_prompt, get_auto_reply_from_deepseek,get_auto_reply_from_openrouter
from app.utils.websocket_registry import register_websocket, unregister_websocket
from app.utils.mem0 import mem0_add_memory , search_memory
from app.utils.permissions import check_message_limit
from app.utils.payg import PlanEnum, report_usage
from app.utils.permissions import increment_message_count, check_message_limit

websocket_router = APIRouter()




@websocket_router.websocket("/ws/chat")
async def chat(websocket: WebSocket, db: Session = Depends(get_db)):
    user = await get_user_from_websocket(websocket)
    
    if not user:
        await websocket.close()
        unregister_websocket(user.id if user else None)
        return
    await websocket.accept()
    register_websocket(user.id, websocket)

    subscription = db.query(Subscription).filter_by(user_id=user.id).first()
    if not subscription:
        await websocket.send_json({
            "type": "error",
            "message": "Aucun abonnement trouvé pour cet utilisateur.",
            "timestamp": datetime.utcnow().isoformat()
        })
        await websocket.close()
        unregister_websocket(user.id)
        return
    
    if hasattr(subscription, "status") and subscription.status != "active":
        await websocket.send_json({
            "type": "error",
            "message": "Votre abonnement n'est pas actif. Merci de le réactiver pour utiliser le service.",
            "timestamp": datetime.utcnow().isoformat()
        })
        await websocket.close()
        unregister_websocket(user.id)
        return

    if not check_message_limit(subscription, db):
        await websocket.send_json({
            "type": "limit_reached",
            "message": "Je crois qu’on a fait le plein de papotages pour ce mois… "
                    "Mais promis, je serai là dès que tu recharges. Tu vas me manquer ! 💙",
            "timestamp": datetime.utcnow().isoformat()
        })
        await websocket.close()
        unregister_websocket(user.id)
        print(f"Limite de messages atteinte pour l'utilisateur {user.id}")
        return
    
    

    subscription.message_count += 1
    db.commit()

    # --- REPORT USAGE STRIPE ---
    if subscription.plan == PlanEnum.PAYG and subscription.stripe_subscription_item_messages:
        try:
            # Incrémente de 1 l'usage messages sur Stripe
            report_usage(
                subscription_item_id=subscription.stripe_subscription_item_messages,
                quantity=1,
                increment=True
            )
        except Exception as e:
            print(f"Erreur lors du report d'usage messages à Stripe : {e}")

    

    try:
        while True:
            try:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                print(f"Message reçu : {message_data}")
            except Exception as e:
                print(f"Erreur réception JSON : {e}\n{traceback.format_exc()}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"Erreur de réception ou JSON invalide : {str(e)}",
                    "timestamp": datetime.utcnow().isoformat()
                })
                continue

            # Validation du bot_id
            bot_id_str = message_data.get("bot_id")
            try:
                bot_id = UUID(bot_id_str)
            except Exception:
                print(f"Erreur bot_id invalide : {bot_id_str}")
                await websocket.send_json({
                    "type": "error",
                    "message": "bot_id manquant ou invalide",
                    "timestamp": datetime.utcnow().isoformat()
                })
                continue

            # Récupération ou création de la conversation unique user/bot
            conversation = db.query(Conversation).filter_by(user_id=user.id, bot_id=bot_id).first()
            if not conversation:
                conversation = Conversation(user_id=user.id, bot_id=bot_id)
                db.add(conversation)
                db.commit()
                db.refresh(conversation)

            timestamp = datetime.utcnow()

            # --- Enregistrement message utilisateur ---
            user_message = Message(
                user_id=user.id,
                content=message_data.get("content", ""),
                conversation_id=conversation.id,
                timestamp=timestamp
            )
            db.add(user_message)
            db.commit()

            

            # --- Construction du prompt avec souvenirs etc. ---
            souvenirs = retrieve_contextual_memories(
                user_message=user_message.content,
                conversation_id=str(conversation.id),
                db=db,
            )

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
                    "date": msg.created_at.strftime("%Y-%m-%d %H:%M:%S")  # Conversion explicite
                }
                for msg in reversed(messages_db)
            ]
            print(f"Messages récents : {messages_recents}")

            memories = db.query(MemoryEntry).filter(MemoryEntry.conversation_id == conversation.id).all()
            personal_info = "\n".join(f"- {m.content}" for m in memories if m.type == MemoryType.PERSONAL) or "Aucune info personnelle"

            directives_entries = db.query(MemoryEntry).filter(
                MemoryEntry.conversation_id == conversation.id,
                MemoryEntry.type == MemoryType.DIRECTIVE
            ).order_by(MemoryEntry.importance.desc(), MemoryEntry.created_at.desc()).all()
            directives_text = "\n".join(f"- {d.content}" for d in directives_entries) or "Aucune directive"

            now = datetime.utcnow()
            soon = now + timedelta(days=7)
            events_soon = db.query(MemoryEntry).filter(
                MemoryEntry.type == MemoryType.EVENT,
                MemoryEntry.event_date != None,
                MemoryEntry.event_date.between(now, soon)
            ).all()
            event_summary = "\n".join(
                f"- ({e.event_date.strftime('%Y-%m-%d')}) {e.content}" for e in events_soon
            ) or "Aucun événement prévu"

            try:
                prompt = build_prompt(
                    messages_recents,
                    souvenirs,
                    directives_text,
                    personal_info,
                    event_summary,
                    bot_id,
                    get_session()
                )
                print(f"Prompt construit : {prompt[:100]}...")
                json.dumps(prompt)  # Test de sérialisation
            except Exception as e:
                print(f"Erreur build_prompt : {e}\n{traceback.format_exc()}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"Erreur lors de la construction du prompt : {str(e)}",
                    "timestamp": datetime.utcnow().isoformat()
                })
                continue

            dernier_message = {
                "auteur": user.name,
                "contenu": user_message.content,
                "date": timestamp.strftime("%Y-%m-%d %H:%M:%S"),  # Conversion explicite
                "user_id": str(user.id),
                "conversation_id": str(conversation.id)
            }
            print(f"Dernier message : {dernier_message}")

            # --- Appel DeepSeek pour réponse automatique ---
            print("Appel DeepSeek")
            try:
                auto_reply = get_auto_reply_from_deepseek(prompt, conversation.id, dernier_message, db)
                print(f"Réponse DeepSeek : {auto_reply}")
                json.dumps(auto_reply)  # Test de sérialisation
            except Exception as e:
                print(f"Erreur DeepSeek : {e}\n{traceback.format_exc()}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"Erreur DeepSeek : {str(e)}",
                    "timestamp": datetime.utcnow().isoformat()
                })
                continue

            if "error" in auto_reply:
                print(f"Erreur dans auto_reply : {auto_reply['error']}")
                await websocket.send_json({
                    "type": "error",
                    "message": auto_reply["error"],
                    "timestamp": datetime.utcnow().isoformat()
                })
                continue

            

            # --- Traitement des actions ---
            actions = auto_reply.get("actions", [])
            actions_immediates = []

            for action_data in actions:
                action_type = action_data.get("type", "")
                if action_type == "repondre":
                    print(f"Action immédiate : {action_data}")
                    actions_immediates.append(action_data)
                elif action_type == "repondre_delay":
                    print(f"Action différée : {action_data}")
                    try:
                        date_str = action_data.get("date", "")
                        if date_str.endswith("Z"):
                            date_str = date_str.replace("Z", "+00:00")
                        date_action = datetime.fromisoformat(date_str)
                    except Exception as e:
                        print(f"Erreur conversion date_action : {e}")
                        date_action = datetime.utcnow()

                    future = FutureAction(
                        conversation_id=conversation.id,
                        action=action_type,
                        date_action=date_action,
                        future_message=action_data.get("message", "")
                    )
                    db.add(future)

            db.commit()
            futures = db.query(FutureAction).all()
            print(f"Future actions en base : {futures}")

            # --- Enregistrement du message bot ---
            if actions_immediates:
                reply_message = actions_immediates[0].get("message", "Désolé, une erreur est survenue.")
            else:
                reply_message = "vu"

            bot_message = Message(
                user_id=bot_id,
                content=reply_message,
                conversation_id=conversation.id,
                timestamp=datetime.utcnow()
            )
            db.add(bot_message)
            db.commit()

            # --- Envoi de la réponse ---
            try:
                response = {
                    "type": "reponse",
                    "message": reply_message,
                    "timestamp": bot_message.created_at.isoformat()
                }
                json.dumps(response)  # Test de sérialisation
                await websocket.send_json(response)
            except Exception as e:
                print(f"Erreur envoi JSON : {e}\n{traceback.format_exc()}")
                raise
            
            # --- Ajout mémoire Mem0 pour message utilisateur ---
            try:
                mem0_add_memory(
                    db=db,
                    conversation_id=conversation.id,
                    content=user_message.content,
                    memory_type=MemoryType.SHORT,
                    importance=MemoryImportance.MEDIUM,
                    user_id=str(user.id),
                    timestamp=timestamp
                )
            except Exception as e:
                print(f"Erreur ajout mémoire Mem0 message utilisateur : {e}\n{traceback.format_exc()}")
                await websocket.send_json({
                    "type": "warning",
                    "message": f"Erreur lors de l'ajout de la mémoire utilisateur : {str(e)}",
                    "timestamp": datetime.utcnow().isoformat()
                })

            # --- Traitement des entrées MemoryEntry du JSON ---
            memory_entries = auto_reply.get("MemoryEntry", [])
            for memory_entry_data in memory_entries:
                try:
                    event_date_str = memory_entry_data.get("event_date")
                    event_date = None
                    if event_date_str:
                        try:
                            if event_date_str.endswith("Z"):
                                event_date_str = event_date_str.replace("Z", "+00:00")
                            event_date = datetime.fromisoformat(event_date_str)
                        except ValueError as e:
                            print(f"Erreur conversion event_date : {e}")
                            event_date = None

                    mem0_add_memory(
                        db=db,
                        conversation_id=conversation.id,
                        content=memory_entry_data.get("contenu", ""),
                        memory_type=memory_entry_data.get("type", "other"),
                        importance=memory_entry_data.get("importance", "medium"),
                        user_id=str(user.id),
                        timestamp=datetime.utcnow(),
                        event_date=event_date
                    )
                except Exception as e:
                    print(f"Erreur ajout mémoire Mem0 pour MemoryEntry : {e}\n{traceback.format_exc()}")
                    await websocket.send_json({
                        "type": "warning",
                        "message": f"Erreur lors de l'ajout de la mémoire DeepSeek : {str(e)}",
                        "timestamp": datetime.utcnow().isoformat()
                    })

        
            # --- Ajout mémoire Mem0 pour message bot (SHORT, MEDIUM) ---
            try:
                mem0_add_memory(
                    db=db,
                    conversation_id=conversation.id,
                    content=bot_message.content,
                    memory_type=MemoryType.SHORT,
                    importance=MemoryImportance.MEDIUM,
                    user_id=str(user.id),
                    timestamp=bot_message.created_at
                )
            except Exception as e:
                print(f"Erreur ajout mémoire Mem0 message bot : {e}\n{traceback.format_exc()}")
                await websocket.send_json({
                    "type": "warning",
                    "message": f"Erreur lors de l'ajout de la mémoire bot : {str(e)}",
                    "timestamp": datetime.utcnow().isoformat()
                })

            

    except WebSocketDisconnect:
        unregister_websocket(user.id)
        print(f"Déconnexion de l'utilisateur {user.id}")

    except Exception as e:
        print(f"Erreur WebSocket : {str(e)}\n{traceback.format_exc()}")
        await websocket.send_json({
            "type": "error",
            "message": f"Erreur interne : {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        })
        await websocket.close()
        unregister_websocket(user.id)

# Fonctions utiles

def error_msg(message: str) -> dict:
    return {
        "type": "error",
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }

def format_list(items: list[str], default: str = "Aucune donnée.") -> str:
    return "\n".join(f"- {item}" for item in items) if items else default


def extract_json_block(content: str):
    """
    Extrait un bloc JSON contenu entre des balises ```json ... ``` dans une chaîne markdown.
    """
    match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
    if not match:
        raise ValueError("Aucun bloc JSON valide trouvé.")
    json_str = match.group(1)
    return json.loads(json_str)

def get_all_memories(conversation_id: UUID, db: Session) -> List[MemoryEntry]:
    """
    Récupère toutes les entrées mémoire liées à une conversation donnée, triées par importance (desc) puis par date (desc).
    
    Args:
        conversation_id (UUID): ID de la conversation.
        db (Session): Session SQLAlchemy.

    Returns:
        List[MemoryEntry]: Liste des souvenirs associés.
    """
    try:
        memories = db.query(MemoryEntry).filter(
            MemoryEntry.conversation_id == conversation_id
        ).order_by(
            MemoryEntry.importance.desc(),  # d'abord les plus importantes
            MemoryEntry.created_at.desc()   # puis les plus récentes
        ).all()

        return memories

    except Exception as e:
        print(f"[get_all_memories] Erreur lors de la récupération des souvenirs : {e}")
        return []
    


def retrieve_contextual_memories(user_message: str, conversation_id: str, db: Session) -> List[MemoryEntry]:
    """
    Combine recherche vectorielle Mem0 et fallback lexical.
    Retourne des objets MemoryEntry SQLModel.
    """
    souvenirs_vector = []
    souvenirs_lexical = []

    try:
        memories_content = search_memory(
            user_message=user_message,
            conversation_id=conversation_id,
            type_filter=[
                MemoryType.SHORT,
                MemoryType.LONG,
                MemoryType.BEHAVIOR,
                MemoryType.FACT,
                MemoryType.EVENT,
                MemoryType.OTHER,
            ],
            importance_filter=[
                MemoryImportance.HIGH,
                MemoryImportance.CRITICAL,
                MemoryImportance.MEDIUM,
            ]
        )

        # Convertit les contenus texte en objets MemoryEntry de la base si présents
        all_db_memories = get_all_memories(UUID(conversation_id), db)
        souvenirs_vector = [
            m for m in all_db_memories
            if m.content in memories_content
        ]
        print(f"[Mem0 search] {len(souvenirs_vector)} souvenirs vectoriels : {[m.content for m in souvenirs_vector]}")

    except Exception as e:
        import traceback
        print(f"[Mem0 search] Erreur : {e}\n{traceback.format_exc()}")

    try:
        mots_cles = ["anniversaire", "rendez-vous", "souvenir", "date", "lieu", "préférence"]
        souvenirs_lexical = [
            m for m in all_db_memories
            if any(k in m.content.lower() for k in mots_cles)
            and m.id not in {s.id for s in souvenirs_vector}
        ]
        if souvenirs_lexical:
            print(f"[Fallback lexical] {len(souvenirs_lexical)} souvenirs : {[m.content for m in souvenirs_lexical]}")
    except Exception as e:
        import traceback
        print(f"[Fallback lexical] Erreur : {e}\n{traceback.format_exc()}")

    return souvenirs_vector + souvenirs_lexical