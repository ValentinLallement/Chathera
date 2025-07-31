import uuid
import asyncio
import re
import json

from typing import List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect,Depends
from sqlmodel import Session, select
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import uuid4, UUID
from datetime import datetime,timedelta,timezone

from app.db.models.models import Message, Conversation, FutureAction, MemoryType, MemoryImportance, MemoryEntry, Subscription
from app.database import get_db,async_session
from app.websocket.auth_ws import get_user_from_websocket
from app.utils.auto_reply import build_prompt, get_auto_reply_from_deepseek,get_auto_reply_from_openrouter
from app.utils.websocket_registry import register_websocket, unregister_websocket
from app.utils.mem0 import mem0_add_memory , search_memory
from app.utils.permissions import check_message_limit
from app.utils.payg import PlanEnum, report_usage
from app.utils.permissions import check_message_limit,check_bot_access

websocket_router = APIRouter()




@websocket_router.websocket("/ws/chat")
async def chat(websocket: WebSocket):
    await websocket.accept()

    user = await get_user_from_websocket(websocket)
    if not user:
        print("Connexion WebSocket rejetée : utilisateur non authentifié")
        await websocket.close(code=1008)
        return

    register_websocket(user.id, websocket)
    print(f"Utilisateur {user.id} connecté au WebSocket")

    try:
        async with async_session() as db:
            while True:
                data = await websocket.receive_text()
                try:
                    message_data = json.loads(data)
                except json.JSONDecodeError as e:
                    print(f"Erreur de décodage JSON : {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": "Format de message invalide",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                    continue

                content = message_data.get("content", "")
                if not content:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Le contenu du message ne peut pas être vide",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                    continue

                stmt_sub = select(Subscription).where(Subscription.user_id == user.id)
                result_sub = await db.execute(stmt_sub)
                subscription = result_sub.scalars().first()

                if not subscription:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Aucun abonnement.",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                    await websocket.close(code=1008)
                    break

                if getattr(subscription, "status", None) != "active":
                    await websocket.send_json({
                        "type": "error",
                        "message": "Abonnement inactif.",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                    await websocket.close(code=1008)
                    break

                if not await check_message_limit(subscription, db):
                    await websocket.send_json({
                        "type": "limit_reached",
                        "message": "Limite atteinte.",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                    await websocket.close(code=1008)
                    break

                try:
                    bot_id = UUID(message_data.get("bot_id"))
                except (ValueError, TypeError) as e:
                    print(f"Erreur bot_id invalide : {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": "bot_id invalide",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                    continue
                    
                has_access = await check_bot_access(db, user.id, bot_id, subscription.plan)

                if not has_access:
                    await websocket.send_json({
                        "type": "access_denied",
                        "message": "Accès refusé : votre abonnement ne permet plus d'utiliser ce bot.",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                    continue
                    
                
                subscription.message_count += 1
                if subscription.plan == PlanEnum.FREE:
                    subscription.free_message_count += 1
                await db.commit()

                if subscription.plan == PlanEnum.PAYG and subscription.stripe_subscription_item_messages:
                    try:
                        report_usage(subscription_item_id=subscription.stripe_subscription_item_messages, quantity=1, increment=True)
                    except Exception as e:
                        print(f"Erreur Stripe : {e}")

                stmt_conv = select(Conversation).where(
                    Conversation.user_id == user.id,
                    Conversation.bot_id == bot_id
                )
                result_conv = await db.execute(stmt_conv)
                conversation = result_conv.scalars().first()

                if not conversation:
                    conversation = Conversation(user_id=user.id, bot_id=bot_id)
                    db.add(conversation)
                    await db.commit()
                    await db.refresh(conversation)

                timestamp = datetime.now(timezone.utc)
                user_msg = Message(
                    user_id=user.id,
                    content=content,
                    conversation_id=conversation.id,
                    created_at=timestamp
                )
                db.add(user_msg)
                await db.commit()

                try:
                    souvenirs = await retrieve_contextual_memories(
                        user_message=user_msg.content,
                        conversation_id=str(conversation.id),
                        db=db
                    )
                except Exception as e:
                    print(f"Erreur lors de la récupération des souvenirs : {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": "Erreur lors de la récupération des souvenirs",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                    continue

                stmt_msgs = select(Message).where(Message.conversation_id == conversation.id).order_by(Message.created_at.desc()).limit(10)
                result_msgs = await db.execute(stmt_msgs)
                messages_db = result_msgs.scalars().all()

                messages_recents = [
                    {
                        "auteur": user.name if m.user_id == user.id else "IA",
                        "contenu": m.content,
                        "date": m.created_at.strftime("%Y-%m-%d %H:%M:%S")
                    } for m in reversed(messages_db)
                ]

                stmt_personal = select(MemoryEntry).where(
                    MemoryEntry.conversation_id == conversation.id,
                    MemoryEntry.type == MemoryType.PERSONAL
                )
                result_personal = await db.execute(stmt_personal)
                personal_info_list = result_personal.scalars().all()
                personal_info = "\n".join(f"- {m.content}" for m in personal_info_list) or "Aucune info"

                stmt_directives = select(MemoryEntry).where(
                    MemoryEntry.conversation_id == conversation.id,
                    MemoryEntry.type == MemoryType.DIRECTIVE
                ).order_by(MemoryEntry.importance.desc(), MemoryEntry.created_at.desc())
                result_directives = await db.execute(stmt_directives)
                directives_list = result_directives.scalars().all()
                directives = "\n".join(f"- {d.content}" for d in directives_list) or "Aucune directive"

                now, soon = datetime.now(timezone.utc), datetime.now(timezone.utc) + timedelta(days=7)
                stmt_events = select(MemoryEntry).where(
                    MemoryEntry.type == MemoryType.EVENT,
                    MemoryEntry.event_date != None,
                    MemoryEntry.event_date.between(now, soon)
                )
                result_events = await db.execute(stmt_events)
                events = result_events.scalars().all()
                event_summary = "\n".join(f"- ({e.event_date.strftime('%Y-%m-%d')}) {e.content}" for e in events) or "Aucun événement"

                try:
                    prompt = await build_prompt(
                        messages_recents,
                        souvenirs,
                        personal_info,
                        directives,
                        event_summary,
                        bot_id,
                        db
                    )
                except Exception as e:
                    print(f"Erreur lors de la construction du prompt : {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": "Erreur lors de la construction du prompt",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                    continue

                dernier_msg = {
                    "auteur": user.name,
                    "contenu": user_msg.content,
                    "date": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "user_id": str(user.id),
                    "conversation_id": str(conversation.id)
                }

                try:
                    auto_reply = await get_auto_reply_from_deepseek(prompt, conversation.id, dernier_msg, db)
                    if "error" in auto_reply:
                        await websocket.send_json({
                            "type": "error",
                            "message": auto_reply["error"],
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
                        continue
                except Exception as e:
                    print(f"Erreur lors de l'appel à get_auto_reply_from_deepseek : {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": "Erreur lors de la génération de la réponse",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                    continue

                actions = auto_reply.get("actions", [])
                reply_msg = next((a.get("message") for a in actions if a.get("type") == "repondre"), "vu")

                for act in actions:
                    if act.get("type") == "repondre_delay":
                        try:
                            act_date = datetime.fromisoformat(act["date"].replace("Z", "+00:00"))
                            act_date = act_date.astimezone(timezone.utc).replace(tzinfo=None)
                        except Exception as e:
                            print(f"Erreur de parsing de date pour action différée : {e}")
                            act_date = datetime.now(timezone.utc)

                        db.add(FutureAction(
                            conversation_id=conversation.id,
                            action="repondre_delay",
                            date_action=act_date,
                            future_message=act.get("message")
                        ))

                bot_msg = Message(
                    user_id=bot_id,
                    content=reply_msg,
                    conversation_id=conversation.id,
                    created_at=datetime.now(timezone.utc)
                )
                db.add(bot_msg)
                await db.commit()

                await websocket.send_json({
                    "type": "reponse",
                    "message": reply_msg,
                    "timestamp": bot_msg.created_at.isoformat()
                })

                try:
                    await mem0_add_memory(db, conversation.id, user_msg.content, MemoryType.SHORT, MemoryImportance.MEDIUM, str(user.id), timestamp)
                    await mem0_add_memory(db, conversation.id, bot_msg.content, MemoryType.SHORT, MemoryImportance.MEDIUM, str(user.id), bot_msg.created_at)
                except Exception as e:
                    print(f"Erreur lors de l'ajout à la mémoire : {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": "Erreur lors de la mise à jour de la mémoire",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                    continue

                for m in auto_reply.get("MemoryEntry", []):
                    try:
                        event_date = datetime.fromisoformat(m["event_date"].replace("Z", "+00:00")) if m.get("event_date") else None
                    except Exception as e:
                        print(f"Erreur de parsing de date pour MemoryEntry : {e}")
                        event_date = None
                    try:
                        await mem0_add_memory(
                            db,
                            conversation.id,
                            m.get("contenu", ""),
                            m.get("type", "other"),
                            m.get("importance", "medium"),
                            str(user.id),
                            datetime.now(timezone.utc),
                            event_date
                        )
                    except Exception as e:
                        print(f"Erreur lors de l'ajout de MemoryEntry : {e}")
                        await websocket.send_json({
                            "type": "error",
                            "message": "Erreur lors de l'ajout de MemoryEntry",
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
                        continue

    except WebSocketDisconnect:
        print(f"Utilisateur {user.id} déconnecté du WebSocket")
        unregister_websocket(user.id)
    except Exception as e:
        print(f"Erreur dans la gestion du WebSocket pour {user.id}: {e}")
        unregister_websocket(user.id)
        await websocket.close(code=1008)
        return

# Fonctions utiles

def error_msg(message: str) -> dict:
    return {
        "type": "error",
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat()
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

async def get_all_memories(conversation_id: UUID, db: AsyncSession) -> List[MemoryEntry]:
    """
    Récupère toutes les entrées mémoire liées à une conversation donnée, triées par importance (desc) puis par date (desc).
    """
    try:
        statement = select(MemoryEntry).where(
            MemoryEntry.conversation_id == conversation_id
        ).order_by(
            MemoryEntry.importance.desc(),
            MemoryEntry.created_at.desc()
        )

        results = await db.execute(statement)  # Ajout de await
        return results.scalars().all()

    except Exception as e:
        print(f"[get_all_memories] Erreur lors de la récupération des souvenirs : {e}")
        return []
    


async def retrieve_contextual_memories(user_message: str, conversation_id: str, db: AsyncSession) -> List[MemoryEntry]:
    """
    Combine recherche vectorielle Mem0 et fallback lexical.
    Retourne des objets MemoryEntry SQLModel.
    """
    souvenirs_vector = []
    souvenirs_lexical = []

    try:
        memories_content = await search_memory(  # Ajout de await
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
        all_db_memories = await get_all_memories(UUID(conversation_id), db)  # Ajout de await
        souvenirs_vector = [
            m for m in all_db_memories
            if m.content in memories_content
        ]
        print(f"[Mem0 search] {len(souvenirs_vector)} souvenirs vectoriels : {[m.content for m in souvenirs_vector]}")

    except Exception as e:
        print(f"[Mem0 search] Erreur : {e}")

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
        print(f"[Fallback lexical] Erreur : {e}")

    return souvenirs_vector + souvenirs_lexical
