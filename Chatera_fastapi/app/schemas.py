from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlmodel import SQLModel

# ----------------------------- Utilisateur -----------------------------
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str
    name: str

    class Config:
        orm_mode = True

class User(UserBase):
    id: UUID

    class Config:
        orm_mode = True

# ----------------------------- Authentification -----------------------------
class Token(BaseModel):
    access_token: str
    token_type: str

# ----------------------------- Message -----------------------------
class MessageBase(BaseModel):
    content: str
    created_at: datetime  # on utilise `created_at` pour refléter la base de données

class Message(MessageBase):
    id: UUID
    user_id: UUID

    class Config:
        orm_mode = True

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