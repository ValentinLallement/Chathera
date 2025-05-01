from sqlalchemy.orm import Session
from . import models, schemas,auth
from passlib.context import CryptContext
from app.models import Conversation, Message, Memory, FutureAction
from uuid import UUID
from datetime import datetime





pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.hash_password(user.password)  # Hachez le mot de passe avant de l'enregistrer
    db_user = models.User(
        username=user.username,
        email=user.email,
        password=hashed_password,  # Utilisez le mot de passe haché
        name=user.name  # Ajoutez ici le champ name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()



#------------------------------------------------------------------------



# ✅ Conversation
def create_conversation(session: Session, user_id: UUID) -> Conversation:
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


def get_conversation_by_id(session: Session, conversation_id: UUID) -> Conversation | None:
    return session.get(Conversation, conversation_id)


# ✅ Message
def create_message(session: Session, user_id: UUID, conversation_id: UUID, content: str) -> Message:
    message = Message(user_id=user_id, conversation_id=conversation_id, content=content)
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


# ✅ Memory
def create_memory(session: Session, user_id: UUID, type_: str, contenu: str) -> Memory:
    memory = Memory(user_id=user_id, type=type_, contenu=contenu)
    session.add(memory)
    session.commit()
    session.refresh(memory)
    return memory


# ✅ FutureAction
def create_future_action(
    session: Session,
    conversation_id: UUID,
    action: str,
    date_action: datetime,
    future_message: str
) -> FutureAction:
    fa = FutureAction(
        conversation_id=conversation_id,
        action=action,
        date_action=date_action,
        future_message=future_message
    )
    session.add(fa)
    session.commit()
    session.refresh(fa)
    return fa

def get_messages_by_user(db: Session, user_id: UUID) -> list[Message]:
    return db.query(Message).filter(Message.user_id == user_id).all()