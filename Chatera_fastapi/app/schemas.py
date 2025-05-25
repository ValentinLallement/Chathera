from pydantic import BaseModel
from sqlmodel import SQLModel

from typing import Optional, List
from uuid import UUID
from datetime import datetime


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

    class Config:
        from_attributes = True

class GoogleLogin(BaseModel):
    token: str  # Token ID JWT envoyé par le client Google
    access_token: str

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

# ----------------------------- IA & Prompts -----------------------------
class AutoReplyResponse(BaseModel):
    nouvelle_memoire: List[dict]
    message: str
    action: str
    date_action: Optional[str]
    future_action: Optional[str]
    date_future_action: Optional[str]
    future_message: Optional[str]

class PromptRequest(BaseModel):
    prompt: str

class MessageRequest(BaseModel):
    messages_recents: List[dict]
    dernier_message: dict


class CreateBotRequest(BaseModel):
    name: str
    