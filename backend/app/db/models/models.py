import uuid
import enum

from datetime import datetime,date, timedelta
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, SQLModel, Relationship

from sqlalchemy import Column, String, UniqueConstraint, DateTime, Text, Enum, ForeignKey, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from sqlalchemy.dialects.postgresql import UUID as SA_UUID
from sqlalchemy.dialects.postgresql import JSONB

from pydantic import BaseModel, root_validator
from pydantic import ConfigDict

from app.utils.payg import PlanEnum

if TYPE_CHECKING:
    from .models import Conversation, Message

Base = declarative_base()
# --------------  user  -----------------

class User(SQLModel, table=True):
    __tablename__ = "user"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    is_active: bool = Field(default=True, nullable=False)
    username: Optional[str] = None
    email: str
    is_verified: bool = Field(default=False)
    password: Optional[str] = None  
    name: Optional[str] = None 

    profile_picture: Optional[str] = None  # URL de la photo de profil Google
    google_sub: Optional[str] = None  # ID Google (subject) unique, pour reconnaitre l’utilisateur Google

    conversations: List["Conversation"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    bots: List["Bot"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    subscriptions: List["Subscription"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "lazy": "selectin"
        }
    )

    stripe_customer_id: Optional[str] = Field(default=None, index=True, nullable=True)

    legal_consent: Optional["UserLegalConsent"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

class UserDraft(SQLModel, table=True):
    __tablename__ = "user_drafts"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: Optional[str] = Field(index=True)
    email: str = Field(index=True)
    password: str  # Hashed
    name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserLegalConsent(SQLModel, table=True):
    __tablename__ = "user_legal_consent"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")

    accepted_terms: bool = Field(default=False)
    accepted_terms_at: Optional[datetime] = None

    accepted_privacy: bool = Field(default=False)
    accepted_privacy_at: Optional[datetime] = None

    accepted_cookies: bool = Field(default=False)
    accepted_cookies_at: Optional[datetime] = None

    user: Optional["User"] = Relationship(back_populates="legal_consent")


class EmailVerificationCode(SQLModel, table=True):
    __tablename__ = "email_verification_codes"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(index=True, nullable=False)
    code: str = Field(nullable=False)
    is_used: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(minutes=10))

# --------------  message  -----------------

class Message(SQLModel, table=True):
    __tablename__ = "messages"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id")

    conversation: Optional["Conversation"] = Relationship(back_populates="messages")

# ----------------  action future  ---------------

class FutureAction(SQLModel, table=True):
    __tablename__ = "future_actions"

    # Pydantic V2 configuration
    model_config = ConfigDict(
        arbitrary_types_allowed=True,  # Allow arbitrary types like uuid.UUID
        from_attributes=True          # Enable ORM mode
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id", nullable=False)
    action: str = Field(nullable=False)
    date_action: datetime = Field(sa_column=Column(DateTime(timezone=False), nullable=False))
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
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    memory_entries: List["MemoryEntry"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    future_actions: List[FutureAction] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    class Config:
        arbitrary_types_allowed = True

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

class TypeEnum(str, Enum):
    free = "Free"
    premium = "Premium"
    payg = "Payg"


class Bot(SQLModel, table=True):
    __tablename__ = "bot"
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(nullable=False)

    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    user: "User" = Relationship(back_populates="bots")

    conversations: List["Conversation"] = Relationship(
        back_populates="bot",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    emotion: Optional["CompanionEmotion"] = Relationship(
        back_populates="bot",
        sa_relationship_kwargs={"uselist": False, "cascade": "all, delete-orphan"}
    )
    
    personality: PersonalityEnum = Field(default=PersonalityEnum.sweet, nullable=True)
    dependency_level: int = Field(default=3, ge=1, le=5, nullable=True)
    gender: GenderEnum = Field(default=GenderEnum.female, nullable=True)

    avatar_url: Optional[str] = Field(default=None, max_length=300)
    url : Optional[str] = Field(default=None, max_length=300)

    type: TypeEnum = Field(default=TypeEnum.free, nullable=True)

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=True)

class CompanionEmotion(SQLModel, table=True):
    __tablename__ = "companion_emotions"

    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    bot_id: UUID = Field(foreign_key="bot.id", index=True, unique=True)
    bot: "Bot" = Relationship(back_populates="emotion")

    mood: str
    energy: str
    style: str

    since: datetime = Field(default_factory=datetime.utcnow)
    duration: timedelta = Field(default_factory=lambda: timedelta(days=3))
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

class SubscriptionStatus(str, Enum):
    active = "active"
    canceled = "canceled"
    incomplete = "incomplete"
    incomplete_expired = "incomplete_expired"
    past_due = "past_due"
    trialing = "trialing"
    unpaid = "unpaid"
    paused = "paused"

    
class Subscription(SQLModel, table=True):
    __tablename__ = "subscription"

    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user: Optional["User"] = Relationship(back_populates="subscriptions")
    user_id: UUID = Field(foreign_key="user.id", nullable=False)

    plan: PlanEnum = Field(default=PlanEnum.FREE)    
    start_date: datetime = Field(default_factory=datetime.utcnow)
    message_count: int = Field(default=0)
    free_message_count: int = Field(default=0)
    last_reset: date = Field(default_factory=lambda: datetime.utcnow().date())
    status: SubscriptionStatus = Field(default=SubscriptionStatus.active,nullable=True)
    message_limit: Optional[int] = Field(default=None)

    stripe_subscription_id: Optional[str] = Field(default=None, nullable=True, index=True)

    stripe_subscription_item_messages: Optional[str] = Field(default=None, nullable=True, index=True)
    stripe_subscription_item_bots: Optional[str] = Field(default=None, nullable=True, index=True)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    

class SubscriptionHistory(SQLModel, table=True):
    __tablename__ = "subscription_history"

    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    subscription_id: UUID = Field(foreign_key="subscription.id", nullable=False)

    user_id: UUID = Field(foreign_key="user.id", nullable=False)

    plan: PlanEnum = Field()
    start_date: datetime
    message_count: int = Field(default=0)
    free_message_count: int = Field(default=0)
    last_reset: date
    status: SubscriptionStatus = Field(default=SubscriptionStatus.active,nullable=True)
    message_limit: Optional[int] = Field(default=None)

    stripe_subscription_id: Optional[str] = Field(default=None, nullable=True, index=True)
    stripe_subscription_item_messages: Optional[str] = Field(default=None, nullable=True, index=True)
    stripe_subscription_item_bots: Optional[str] = Field(default=None, nullable=True, index=True)

    recorded_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)

    class Config:
        arbitrary_types_allowed = True

# -------- Pay-as-you-go -----------


class UsageTypeEnum(str, enum.Enum):
    message = "message"
    bot_creation = "bot_creation"


class UsageLog(SQLModel, table=True):
    __tablename__ = "usage_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    bot_id: Optional[UUID] = Field(foreign_key="bot.id", default=None)

    type: UsageTypeEnum = Field(sa_column=Column(
        Enum(UsageTypeEnum, name="usage_type"), nullable=False
    ))

    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Relations optionnelles (utile si tu veux accéder aux objets depuis les logs)
    user: Optional["User"] = Relationship(back_populates=None)
    bot: Optional["Bot"] = Relationship(back_populates=None)



class MonthlyUsage(SQLModel, table=True):
    __tablename__ = "monthly_usage"

    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    
    year: int
    month: int

    total_messages: int = Field(default=0)
    total_bots_created: int = Field(default=0)
    billed: bool = Field(default=False)

    # Relation utile pour accès depuis l'utilisateur si besoin
    user: Optional["User"] = Relationship(back_populates=None)

    # --------- Notification Push ---------------

class PushSubscription(SQLModel, table=True):
    __tablename__ = "push_subscriptions"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    endpoint: str = Field(index=True, unique=True, nullable=False)
    keys: dict = Field(sa_column=Column(JSON, nullable=False))
