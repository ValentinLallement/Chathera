from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas import Message as MessageSchema
from app.crud import get_messages_by_user
from app.dependencies import get_db
from uuid import UUID
router = APIRouter()

@router.get("/users/{user_id}/messages", response_model=List[MessageSchema])
def read_user_messages(user_id: UUID, db: Session = Depends(get_db)):
    messages = get_messages_by_user(db, user_id)
    if not messages:
        raise HTTPException(status_code=404, detail="Aucun message trouvé pour cet utilisateur.")
    return messages