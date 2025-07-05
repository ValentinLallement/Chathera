from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlmodel import Session,select
from sqlalchemy.ext.asyncio import AsyncSession


from typing import List
from uuid import UUID

from app.db.models.models import Message, Conversation, User
from app.auth import get_user_from_token  # ta fonction d’authentification
from app.schemas import Message as MessageSchema
from app.schemas import ConversationRequest
from app.crud import get_messages_by_user
from app.dependencies import get_db

router = APIRouter()

@router.get("/users/{user_id}/messages", response_model=List[MessageSchema])
async def read_user_messages(user_id: UUID, db: AsyncSession = Depends(get_db)):
    messages = await get_messages_by_user(db, user_id)
    
    if not messages:
        raise HTTPException(status_code=404, detail="Aucun message trouvé pour cet utilisateur.")
    
    return messages

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # adapte l’URL selon ta config

@router.post("/conversations/messages", response_model=List[Message])
async def read_conversation_messages(
    request: ConversationRequest,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = await get_user_from_token(token, db, credentials_exception)

    # ✅ Vérifie que la conversation appartient à l'utilisateur
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == request.conversation_id,
            Conversation.user_id == user.id
        )
    )
    conversation = result.scalars().first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation introuvable pour cet utilisateur.")

    # ✅ Récupère les messages associés
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == request.conversation_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()

    if not messages:
        raise HTTPException(status_code=404, detail="Aucun message trouvé pour cette conversation.")

    return messages


@router.get("/conversations", response_model=List[Conversation])
async def read_user_conversations(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = await get_user_from_token(token, db, credentials_exception)

    result = await db.execute(
        select(Conversation).where(Conversation.user_id == user.id)
    )
    conversations = result.scalars().all()

    if not conversations:
        raise HTTPException(status_code=404, detail="Aucune conversation trouvée.")

    return conversations