from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session
from sqlalchemy import select

from typing import List
from uuid import UUID

from app.models import Message, Conversation, User
from app.auth import get_user_from_token  # ta fonction d’authentification
from app.schemas import Message as MessageSchema
from app.schemas import ConversationRequest
from app.crud import get_messages_by_user
from app.dependencies import get_db

router = APIRouter()

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

@router.get("/users/{user_id}/messages", response_model=List[MessageSchema])
def read_user_messages(user_id: UUID, db: Session = Depends(get_db)):
    messages = get_messages_by_user(db, user_id)
    if not messages:
        raise HTTPException(status_code=404, detail="Aucun message trouvé pour cet utilisateur.")
    return messages


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # adapte l’URL selon ta config

@router.post("/conversations/messages", response_model=List[Message])
def read_conversation_messages(
    request: Request,
    body: ConversationRequest,
    db: Session = Depends(get_db)
):
    # 🔐 Lecture du token depuis les cookies
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Token manquant dans les cookies")

    user: User = get_user_from_token(token, db, credentials_exception)

    # ✅ Vérifie que la conversation appartient à l'utilisateur
    conversation = db.execute(
        select(Conversation).where(
            Conversation.id == body.conversation_id,
            Conversation.user_id == user.id
        )
    ).scalars().first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation introuvable pour cet utilisateur.")

    # ✅ Récupère les messages associés
    messages = db.execute(
        select(Message).where(
            Message.conversation_id == body.conversation_id
        ).order_by(Message.created_at)
    ).scalars().all()

    if not messages:
        raise HTTPException(status_code=404, detail="Aucun message trouvé pour cette conversation.")

    return messages


@router.get("/conversations", response_model=List[Conversation])
def read_user_conversations(
    request: Request,
    db: Session = Depends(get_db)
):
    # 🔐 Lecture du token depuis les cookies
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Token manquant dans les cookies")

    user = get_user_from_token(token, db, credentials_exception)

    conversations = db.execute(
        select(Conversation).where(Conversation.user_id == user.id)
    ).scalars().all()

    if not conversations:
        raise HTTPException(status_code=404, detail="Aucune conversation trouvée.")

    return conversations