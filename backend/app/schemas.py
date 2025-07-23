from pydantic import BaseModel,ConfigDict, model_validator, EmailStr, Field
from sqlmodel import SQLModel


from typing import Optional, List, Literal
from uuid import UUID
from datetime import datetime,date
from enum import Enum

from app.utils.payg import PlanEnum



# ----------------------------- Abonnements -----------------------------

class SubscriptionInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    plan: str
    message_count: int
    bot_count: Optional[int] = None
    message_limit: Optional[int]
    free_message_count: int
    status: str
    remaining: Optional[int] = None

    # Champs Stripe live
    stripe_current_period_start: Optional[datetime] = None
    stripe_current_period_end: Optional[datetime] = None
    stripe_cancel_at_period_end: Optional[bool] = None
    stripe_plan_amount_eur: Optional[float] = None
    stripe_currency: Optional[str] = None

class SubscriptionUpdate(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    plan: Optional[PlanEnum] = None
    message_limit: Optional[int] = None

class EmailSchema(BaseModel):
    email: EmailStr
class CheckoutRequest(BaseModel):
    plan: str 

class UserSubscriptionsResponse(BaseModel):
    subscriptions: Optional[SubscriptionInfo]

# ----------------------------- Utilisateur -------------------------------
class UserLogin(BaseModel):
    login: str  # Peut être un email ou un nom d'utilisateur
    password: str


class UserCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: str
    email: str
    password: str
    name: str

class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: Optional[str] = None
    username: Optional[str] = None
    profile_picture: Optional[str] = None
    is_verified: bool = True

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


# ----------------------------- Authentification -------------------------
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# ----------------------------- Message ----------------------------------

class MessageBase(BaseModel):
    content: str
    created_at: datetime  

class Message(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    
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

    @model_validator(mode='before')
    def convert_empty_strings_to_none(cls, data):
        for key, value in data.items():
            if value == '':
                data[key] = None
        return data
    
class PromptRequest(BaseModel):
    prompt: str

class MessageRequest(BaseModel):
    messages_recents: List[dict]
    dernier_message: dict


class CreateBotRequest(BaseModel):
    name: str
    gender: Literal["Male", "Female"]  # ou str si tu veux laisser plus libre
    personality: Literal["Friendly", "Professional", "Casual", "Serious","Sweet"]  # ou str si tu veux laisser plus libre
    
# ----------------------------- Avatar ----------------------------------------

class AvatarPayload(BaseModel):
    bot_id: UUID
    glb_url: str

# ----------------------------- Notification Push -----------------------------

class SubscriptionData(BaseModel):
    endpoint: str
    keys: dict



# ----------------------------- Consent ---------------------------------------

class UserLegalConsentBase(BaseModel):
    accepted_terms: Optional[bool] = None
    accepted_privacy: Optional[bool] = None
    accepted_cookies: Optional[bool] = None

class UserLegalConsentRead(UserLegalConsentBase):
    model_config = ConfigDict(from_attributes=True)
    accepted_terms_at: Optional[datetime]
    accepted_privacy_at: Optional[datetime]
    accepted_cookies_at: Optional[datetime]

