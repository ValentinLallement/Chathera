import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from pydantic import BaseModel, root_validator
from sqlalchemy import Column, String, UniqueConstraint
from uuid import uuid4, UUID
from sqlalchemy.dialects.postgresql import UUID as SA_UUID
from app.db.base import Base
if TYPE_CHECKING:
    from .models import Conversation, Message

# -------------------------------
# Modèle utilisateur
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str
    email: str
    password: str
    name: str  # Ce champ est requis (non-nullable)

    conversations: List["Conversation"] = Relationship(back_populates="user")
    bots: List["Bot"] = Relationship(back_populates="user")

# -------------------------------
# Modèle mémoire
class Memory(SQLModel, table=True):
    __tablename__ = "memory"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id", nullable=False)
    type: str  # "court_terme" ou "long_terme"
    contenu: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relations
    conversation: Optional["Conversation"] = Relationship(back_populates="memories")

# -------------------------------
# Modèle message
class Message(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id")

    conversation: Optional["Conversation"] = Relationship(back_populates="messages")

# -------------------------------
# Modèle conversation
class Conversation(SQLModel, table=True):
    __tablename__ = "conversation"
    __table_args__ = (
        UniqueConstraint("user_id", "bot_id", name="uq_user_bot"),  # Contrainte unique sur user_id et bot_id
        {"sqlite_autoincrement": True},  # Optionnel selon SGBD
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)  # UUID généré automatiquement
    user_id: UUID = Field(foreign_key="user.id", nullable=False)  # User lié à la conversation
    bot_id: UUID = Field(foreign_key="bot.id", nullable=False)    # Bot lié à la conversation
    created_at: datetime = Field(default_factory=datetime.utcnow)  # Date de création de la conversation

    # Relations
    user: Optional["User"] = Relationship(back_populates="conversations")
    bot: Optional["Bot"] = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")
    memories: List["Memory"] = Relationship(back_populates="conversation")

    # Assure-toi d'utiliser le type UUID correct pour SQLAlchemy
    class Config:
        arbitrary_types_allowed = True
# -------------------------------
# Modèle action future
class FutureAction(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id")
    action: str
    date_action: datetime
    future_message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# -------------------------------
# Modèle réponse automatique
class AutoReplyResponse(BaseModel):
    nouvelle_memoire: Optional[List[dict]] = None
    message: Optional[str] = None
    action: Optional[str] = None
    date_action: Optional[datetime] = None
    future_action: Optional[str] = None
    date_future_action: Optional[datetime] = None
    future_message: Optional[str] = None

    @root_validator(pre=True)
    def convert_empty_strings_to_none(cls, values):
        for key, value in values.items():
            if value == '':
                values[key] = None
        return values

# -------------------------------
# Modèle de requête de message
class MessageRequest(BaseModel):
    messages_recents: List[dict]
    dernier_message: dict



# -------------------------------
class Bot(SQLModel, table=True):
    __tablename__ = "bot"
    
    # Id généré automatiquement
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    
    # Nom du bot
    name: str = Field(nullable=False)
    
    # Id de l'utilisateur lié au bot
    user_id: UUID = Field(default=None, foreign_key="user.id", nullable=False)  # Assurez-vous que la relation avec l'utilisateur est bien définie

    # Relation avec la table User
    user: "User" = Relationship(back_populates="bots")  # Définir la relation avec le modèle User

    # Relation avec la conversation
    conversations: List["Conversation"] = Relationship(back_populates="bot")
