from datetime import datetime
from sqlalchemy.orm import Session
from typing import Optional, List, Union
from app.db.models.models import MemoryEntry, MemoryImportance, MemoryType  
from mem0 import Memory
from app.config import MEM0_CONFIG as config

# Initialisation globale mem0 (faire 1 fois au lancement)
mem0 = Memory.from_config(config)

def mem0_add_memory(
    db: Session,
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
        db: session SQLAlchemy.
        conversation_id: ID de la conversation (int ou str).
        content: texte à stocker.
        memory_type: type mémoire (int, MemoryType enum ou str).
        importance: importance mémoire (int, MemoryImportance enum ou str).
        user_id: ID utilisateur (int ou str).
        timestamp: horodatage (datetime UTC). Si None, prend datetime.utcnow().
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
        timestamp = datetime.utcnow()

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
    db.commit()
    db.refresh(memory_entry)

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

def search_memory(
    user_message: str,
    conversation_id: Optional[str] = None,
    type_filter: Optional[List[MemoryType]] = None,
    importance_filter: Optional[List[MemoryImportance]] = None
) -> dict:
    """
    Recherche en mémoire mem0ai avec les filtres, et retourne un dict
    contenant au moins la clé 'results' avec une liste des résultats trouvés.
    """

    # Prépare le query (exemple simple)
    query = user_message

    # Prépare les filtres, adapte selon ton système mem0ai
    filters = {}
    if conversation_id:
        filters["conversation_id"] = conversation_id
    if type_filter:
        filters["type"] = [t.value for t in type_filter]
    if importance_filter:
        filters["importance"] = [i.value for i in importance_filter]

    try:
        # Appelle mem0ai.search() - adapter avec ta vraie fonction
        results = mem0.search(query=query, filters=filters, user_id=conversation_id)
        # Debug : print("Résultats mem0ai.search:", results)

        # Extraction robuste de la liste de résultats
        if isinstance(results, dict) and "results" in results and isinstance(results["results"], list):
            result_list = results["results"]
        elif isinstance(results, list):
            # mem0ai peut retourner directement une liste (par ex. [])
            result_list = results
        else:
            print(f"search_memory: résultats inattendus reçus: {results}")
            result_list = []

        # Extraction des contenus mémoire
        contenus = []
        for r in result_list:
            if isinstance(r, dict) and "memory" in r:
                contenus.append(r["memory"])
            else:
                print(f"search_memory: élément inattendu dans résultats: {r}")

        # Retourne un dict conforme avec la clé 'results'
        return {"results": contenus}

    except Exception as e:
        print(f"Erreur search_memory : {e}")
        return {"results": []}
