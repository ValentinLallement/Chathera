from pydantic import BaseModel,ConfigDict, root_validator, EmailStr, Field
from sqlmodel import SQLModel


from typing import Optional, List, Literal
from uuid import UUID
from datetime import datetime,date
from enum import Enum

from app.utils.payg import PlanEnum



# ----------------------------- Abonnements -----------------------------

class Subscription(BaseModel):
    id: UUID
    user_id: UUID
    plan: str
    start_date: datetime
    message_count: int
    message_limit: Optional[int]
    last_reset: date

    class Config:
        from_attributes = True  

class SubscriptionUpdate(BaseModel):
    plan: Optional[PlanEnum] = None
    message_limit: Optional[int] = None

    class Config:
        arbitrary_types_allowed = True


class CheckoutRequest(BaseModel):
    plan: str 

# ----------------------------- Utilisateur -----------------------------
class UserLogin(BaseModel):
    login: str  # Peut être un email ou un nom d'utilisateur
    password: str
class UserBase(BaseModel):
    username: Optional[str] = None
    email: str

class UserCreate(UserBase):
    password: str
    name: str

    class Config:
        from_attributes = True

class User(UserBase):
    id: UUID
    name: Optional[str] = None
    profile_picture: Optional[str] = None
    subscription: Optional[Subscription] = None

    class Config:
        from_attributes = True

class GoogleLogin(BaseModel):
    token: str  # Token ID JWT envoyé par le client Google
    access_token: str


class UserDeleteRequest(BaseModel):
    password: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)

class EmailCodeVerification(BaseModel):
    email: EmailStr
    code: str

class EmailRequest(BaseModel):
    email: EmailStr


# ----------------------------- Authentification -----------------------------
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# ----------------------------- Message -----------------------------

class MessageBase(BaseModel):
    content: str
    created_at: datetime  # on utilise `created_at` pour refléter la base de données

class Message(MessageBase):
    id: UUID
    user_id: UUID

    class Config:
        from_attributes = True
    
class ConversationRequest(BaseModel):
    conversation_id: UUID

# ----------------------------- IA & Prompts -----------------------------

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
    
class PromptRequest(BaseModel):
    prompt: str

class MessageRequest(BaseModel):
    messages_recents: List[dict]
    dernier_message: dict


class CreateBotRequest(BaseModel):
    name: str
    gender: Literal["Male", "Female"]  # ou str si tu veux laisser plus libre
    personality: Literal["Friendly", "Professional", "Casual", "Serious","Sweet"]  # ou str si tu veux laisser plus libre
    
# ----------------------------- Avatar -----------------------------

class AvatarPayload(BaseModel):
    bot_id: int
    glb_url: str

# ----------------------------- Notification Push -----------------------------

class SubscriptionData(BaseModel):
    endpoint: str
    keys: dict