import uuid
import enum

from datetime import datetime,date
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, SQLModel, Relationship

from sqlalchemy import Column, String, UniqueConstraint, DateTime, Text, Enum, ForeignKey, Integer, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from sqlalchemy.dialects.postgresql import UUID as SA_UUID

from pydantic import BaseModel, root_validator
from pydantic import ConfigDict


from app.utils.payg import PlanEnum
from app.db.base import Base
if TYPE_CHECKING:
    from .models import Conversation, Message

# --------------  user  -----------------

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: Optional[str] = None
    email: str
    password: Optional[str] = None  
    name: Optional[str] = None 

    profile_picture: Optional[str] = None  # URL de la photo de profil Google
    google_sub: Optional[str] = None  # ID Google (subject) unique, pour reconnaitre l’utilisateur Google

    conversations: List["Conversation"] = Relationship(back_populates="user")
    bots: List["Bot"] = Relationship(back_populates="user")

    subscription: Optional["Subscription"] = Relationship(back_populates="user")

# --------------  message  -----------------

class Message(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id")

    conversation: Optional["Conversation"] = Relationship(back_populates="messages")

# ----------------  action future  ---------------

class FutureAction(SQLModel, table=True):
    __tablename__ = "future_actions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id", nullable=False)
    action: str = Field(nullable=False)
    date_action: datetime = Field(nullable=False)
    future_message: str = Field(nullable=False)
    condition: Optional[dict] = Field(sa_column=Column(JSON), default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relation vers Conversation
    conversation: Optional["Conversation"] = Relationship(back_populates="future_actions")

# ----------------  conversation  ---------------
 
class Conversation(SQLModel, table=True):
    __tablename__ = "conversation"
    __table_args__ = (
        UniqueConstraint("user_id", "bot_id", name="uq_user_bot"),
        {"sqlite_autoincrement": True},
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    bot_id: uuid.UUID = Field(foreign_key="bot.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relations
    user: Optional["User"] = Relationship(back_populates="conversations")
    bot: Optional["Bot"] = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")
    memory_entries: List["MemoryEntry"] = Relationship(back_populates="conversation")
    future_actions: List[FutureAction] = Relationship(back_populates="conversation")  # Ici FutureAction doit être défini avant

    class Config:
        arbitrary_types_allowed = True

# ----------------  réponse automatique ---------------

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

# --------------  requête de message  -----------------

class MessageRequest(BaseModel):
    messages_recents: List[dict]
    dernier_message: dict

# ---------------  Bot  ----------------

class PersonalityEnum(str, Enum):
    sweet = "Sweet"
    funny = "Funny"
    romantic = "Romantic"
    serious = "Serious"
    sarcastic = "Sarcastic"

class GenderEnum(str, Enum):
    male = "Male"
    female = "Female"


class Bot(SQLModel, table=True):
    __tablename__ = "bot"
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(nullable=False)

    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    user: "User" = Relationship(back_populates="bots")

    conversations: List["Conversation"] = Relationship(back_populates="bot")

    personality: PersonalityEnum = Field(default=PersonalityEnum.sweet, nullable=True)
    dependency_level: int = Field(default=3, ge=1, le=5, nullable=True)
    gender: GenderEnum = Field(default=GenderEnum.female, nullable=True)

    avatar_url: Optional[str] = Field(default=None, max_length=300)

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=True)

# -----------------  Memory Model  --------------

class MemoryType(str, enum.Enum):
    SHORT = "short"
    LONG = "long"
    BEHAVIOR = "behavior"
    DIRECTIVE = "directive"
    FACT = "fact"
    PERSONAL = "personal"
    EVENT = "event"
    OTHER = "other"

class MemoryImportance(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class MemoryEntry(SQLModel, table=True):
    __tablename__ = "memory_entries"

    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversation.id", nullable=False)
    type: MemoryType = Field(sa_column_kwargs={"default": MemoryType.OTHER})
    importance: MemoryImportance = Field(sa_column_kwargs={"default": MemoryImportance.MEDIUM})
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Date réelle de l'événement si applicable (optionnelle)
    event_date: Optional[datetime] = Field(default=None)

    # Relation inverse
    conversation: Optional[Conversation] = Relationship(back_populates="memory_entries")

# -------- Abonnements -----------

    
class Subscription(SQLModel, table=True):
    __tablename__ = "subscription"

    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", nullable=False)

    plan: PlanEnum = Field(default=PlanEnum.FREE)    
    start_date: datetime = Field(default_factory=datetime.utcnow)
    message_count: int = Field(default=0)
    last_reset: date = Field(default_factory=lambda: datetime.utcnow().date())

    message_limit: Optional[int] = Field(default=None)

    user: Optional["User"] = Relationship(back_populates="subscription")

    model_config = ConfigDict(arbitrary_types_allowed=True)

# -------- Pay-as-you-go -----------


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    bot_id = Column(Integer, ForeignKey("bots.id"), nullable=True)
    type = Column(Enum("message", "bot_creation", name="usage_type"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)



class MonthlyUsage(Base):
    __tablename__ = "monthly_usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    total_messages = Column(Integer, default=0)
    total_bots_created = Column(Integer, default=0)
    billed = Column(Boolean, default=False)