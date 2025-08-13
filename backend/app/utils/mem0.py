from datetime import datetime, timezone
from sqlmodel import Session, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Union
from app.db.models.models import MemoryEntry, MemoryImportance, MemoryType  
from mem0 import Memory
from app.config import mem0

# Initialisation globale mem0 (faire 1 fois au lancement)


async def mem0_add_memory(
    db: AsyncSession,
    conversation_id: Union[int, str],
    content: str,
    memory_type: Union[int, MemoryType, str],
    importance: Union[int, MemoryImportance, str],
    user_id: Union[int, str],
    timestamp: Optional[datetime] = None,
    event_date: Optional[datetime] = None
) -> MemoryEntry:
    """
    Ajoute une entrée mémoire vectorisée dans la base et mem0ai (FAISS).

    Args:
        db: AsyncSession SQLAlchemy.
        conversation_id: ID de la conversation (int ou str).
        content: texte à stocker.
        memory_type: type mémoire (int, MemoryType enum ou str).
        importance: importance mémoire (int, MemoryImportance enum ou str).
        user_id: ID utilisateur (int ou str).
        timestamp: horodatage (datetime UTC). Si None, prend datetime.now(timezone.utc).
        event_date: date de l'événement (datetime, optionnel pour MemoryType.EVENT).

    Returns:
        L’objet MemoryEntry ajouté en base.

    Raises:
        ValueError: Si user_id est vide ou None.
        Exception: Pour les erreurs liées à mem0ai.
    """
    if not user_id:
        raise ValueError("user_id ne peut pas être vide ou None")

    if timestamp is None:
        timestamp = datetime.now(timezone.utc)

    # Convertir memory_type si c'est une chaîne
    if isinstance(memory_type, str):
        memory_type = MemoryType[memory_type.upper()] if memory_type.upper() in MemoryType.__members__ else MemoryType.OTHER
    elif not isinstance(memory_type, MemoryType):
        memory_type = MemoryType(memory_type)

    # Convertir importance si c'est une chaîne
    if isinstance(importance, str):
        importance = MemoryImportance[importance.upper()] if importance.upper() in MemoryImportance.__members__ else MemoryImportance.MEDIUM
    elif not isinstance(importance, MemoryImportance):
        importance = MemoryImportance(importance)

    # Création de l'objet mémoire SQLAlchemy
    memory_entry = MemoryEntry(
        conversation_id=conversation_id,
        user_id=user_id,
        content=content,
        type=memory_type.value,
        importance=importance.value,
        timestamp=timestamp,
        event_date=event_date
    )

    db.add(memory_entry)
    await db.commit()
    await db.refresh(memory_entry)


    # Indexation dans mem0ai
    metadata = {
        "memory_id": memory_entry.id,
        "conversation_id": str(conversation_id),
        "type": memory_type.value,
        "importance": importance.value,
        "timestamp": timestamp.isoformat()
    }
    if event_date:
        metadata["event_date"] = event_date.isoformat()

    try:
        mem0.add(
            messages=[{"role": "user", "content": content}],
            user_id=str(conversation_id),
            metadata=metadata
        )
        print(f"Mémoire ajoutée à mem0ai : memory_id={memory_entry.id}, content={content}")
    except Exception as e:
        print(f"Erreur lors de l'ajout à mem0ai : {e}")
        raise

    return memory_entry

async def search_memory(
    user_message: str,
    conversation_id: Optional[str] = None,
    type_filter: Optional[List[MemoryType]] = None,
    importance_filter: Optional[List[MemoryImportance]] = None,
) -> List[str]:  # on retourne directement une liste de contenus texte
    """
    Recherche dans mem0ai avec filtres et options avancées.
    Retourne une liste de strings (contenus de mémoire).
    """

    filters = {}
    if conversation_id:
        filters["conversation_id"] = conversation_id
    if type_filter:
        filters["type"] = [t.value for t in type_filter]
    if importance_filter:
        filters["importance"] = [i.value for i in importance_filter]

    try:
        results = mem0.search(
            query=user_message,
            filters=filters,
            user_id=conversation_id,
        )

        if isinstance(results, dict) and "results" in results:
            result_list = results["results"]
        elif isinstance(results, list):
            result_list = results
        else:
            print(f"[Mem0] Résultat inattendu: {results}")
            return []

        contenus = []
        for r in result_list:
            if isinstance(r, dict) and "memory" in r:
                contenus.append(r["memory"])
        return contenus

    except Exception as e:
        print(f"[Mem0] Erreur dans search_memory : {e}")
        return []