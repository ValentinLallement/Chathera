from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session
from sqlalchemy import select

from typing import List
from uuid import UUID

from app.models import Message, Conversation, User
from app.auth import get_user_from_token  # ta fonction d’authentification
from app.schemas import Message as MessageSchema
from app.crud import get_messages_by_user
from app.dependencies import get_db

router = APIRouter()

@router.get("/users/{user_id}/messages", response_model=List[MessageSchema])
def read_user_messages(user_id: UUID, db: Session = Depends(get_db)):
    messages = get_messages_by_user(db, user_id)
    if not messages:
        raise HTTPException(status_code=404, detail="Aucun message trouvé pour cet utilisateur.")
    return messages


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # adapte l’URL selon ta config

@router.get("/conversations/{conversation_id}/messages", response_model=List[Message])
def read_conversation_messages(
    conversation_id: UUID,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user: User = get_user_from_token(token, db, credentials_exception)

    # ✅ Recherche la conversation appartenant à l'utilisateur
    conversation = db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user.id
        )
    ).scalars().first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation introuvable pour cet utilisateur.")

    # ✅ Recherche des messages
    messages = db.execute(
        select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at)
    ).scalars().all()

    if not messages:
        raise HTTPException(status_code=404, detail="Aucun message trouvé pour cette conversation.")

    return messages


@router.get("/conversations", response_model=List[Conversation])
def read_user_conversations(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user = get_user_from_token(token, db, credentials_exception)

    conversations = db.execute(
        select(Conversation).where(Conversation.user_id == user.id)
    ).scalars().all()

    if not conversations:
        raise HTTPException(status_code=404, detail="Aucune conversation trouvée.")

    return conversations