import re
import unicodedata

from sqlalchemy.orm import Session

from passlib.context import CryptContext
from uuid import UUID
from datetime import datetime
from typing import Optional

from . import models, schemas,auth
from app.models import Conversation, Message, Memory, FutureAction




#----------------------  User  --------------------------------------------------

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

def get_user_by_username_or_email(db: Session, login: str):
    return db.query(models.User).filter(
        (models.User.username == login) | (models.User.email == login)
    ).first()


#----------------------  GOOGLE  --------------------------------------------------


def generate_unique_username(db: Session, base_username: str) -> str:
    username = base_username
    i = 1
    while db.query(models.User).filter(models.User.username == username).first():
        username = f"{base_username}{i}"
        i += 1
    return username

def normalize_username(name: str) -> str:
    # Supprimer les accents et caractères spéciaux
    name = unicodedata.normalize('NFD', name).encode('ascii', 'ignore').decode('utf-8')
    # Remplacer les espaces par des underscores et mettre en minuscules
    name = re.sub(r'\s+', '_', name).lower()
    # Supprimer les caractères non alphanumériques ou underscore
    name = re.sub(r'[^\w_]', '', name)
    return name

def create_or_update_user_google(db: Session, email: str, name: Optional[str], google_sub: str, picture: Optional[str] = None):
    user = db.query(models.User).filter(models.User.google_sub == google_sub).first()
    if user:
        updated = False
        if name and user.name != name:
            user.name = name
            updated = True
        if picture and user.profile_picture != picture:
            user.profile_picture = picture
            updated = True
        if updated:
            db.commit()
            db.refresh(user)
        return user

    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        updated = False
        if user.google_sub != google_sub:
            user.google_sub = google_sub
            updated = True
        if name and user.name != name:
            user.name = name
            updated = True
        if picture and user.profile_picture != picture:
            print("a")
            user.profile_picture = picture
            updated = True
        if updated:
            db.commit()
            db.refresh(user)
        return user

    # Création nouvel utilisateur
    base_username = normalize_username(name or email.split('@')[0])
    username = generate_unique_username(db, base_username)

    new_user = models.User(
        email=email,
        name=name,
        google_sub=google_sub,
        password=None,
        username=username,
        profile_picture=picture 
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_user_by_google_sub(db: Session, google_sub: str):
    return db.query(models.User).filter(models.User.google_sub == google_sub).first()


#-----------------------------  Conversation  -------------------------------------------



# Conversation
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