import re
import unicodedata
import uuid

from sqlalchemy.orm import Session

from passlib.context import CryptContext
from uuid import UUID
from datetime import datetime
from typing import Optional, Union

from . import models, schemas,auth
from app.models import Conversation, Message, FutureAction, Subscription
from app.models import PlanEnum



#----------------------  User  --------------------------------------------------

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(db: Session, user: schemas.UserCreate):
    # Hacher le mot de passe
    hashed_password = auth.hash_password(user.password)

    # Créer l'utilisateur en base
    db_user = models.User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        name=user.name
    )
    db.add(db_user)
    db.commit()         # Valider pour générer l'ID utilisateur
    db.refresh(db_user) # Récupérer l'ID généré

    # Créer un abonnement free par défaut lié à cet utilisateur
    free_subscription = models.Subscription(
        user_id=db_user.id,
        plan=models.PlanEnum.FREE,
        # start_date, message_count, last_reset, etc. prennent leurs valeurs par défaut
    )
    db.add(free_subscription)
    db.commit()
    db.refresh(free_subscription)

    # Optionnel : lier en mémoire (utile si tu veux accéder à db_user.subscription juste après)
    db_user.subscription = free_subscription

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

    # Créer un abonnement free par défaut pour le nouvel utilisateur
    free_subscription = models.Subscription(
        user_id=new_user.id,
        plan=models.PlanEnum.FREE,
        # start_date, message_count, last_reset, etc. par défaut
    )
    db.add(free_subscription)
    db.commit()
    db.refresh(free_subscription)

    # Optionnel : liaison en mémoire
    new_user.subscription = free_subscription

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


# Message
def create_message(session: Session, user_id: UUID, conversation_id: UUID, content: str) -> Message:
    message = Message(user_id=user_id, conversation_id=conversation_id, content=content)
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


# FutureAction
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


#-----------------------------  Abonnements  -------------------------------------------

def update_user_subscription(
    db: Session,
    user_id: UUID,
    new_plan: Optional[Union[str, PlanEnum]] = None,
    message_limit: Optional[int] = None,
):
    subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()

    if not subscription:
        # Création avec plan FREE par défaut
        subscription = Subscription(
            user_id=user_id,
            plan=PlanEnum.FREE,
            message_limit=None,  # par défaut None car plan free
            message_count=0,
            start_date=datetime.utcnow(),
            last_reset=datetime.utcnow().date()
        )
        db.add(subscription)
        db.flush()  # flush pour générer l'ID si besoin

    if new_plan:
        try:
            if isinstance(new_plan, str):
                new_plan = PlanEnum(new_plan.lower())
        except ValueError:
            raise ValueError(
                f"Invalid plan value '{new_plan}'. Valid values are: {[e.value for e in PlanEnum]}"
            )
        subscription.plan = new_plan
        subscription.start_date = datetime.utcnow()
        subscription.message_count = 0
        subscription.last_reset = datetime.utcnow().date()

    # Gestion message_limit en fonction du plan
    if subscription.plan in {PlanEnum.FREE, PlanEnum.PREMIUM}:
        # On force message_limit à None si le plan est free ou premium, peu importe l'entrée
        subscription.message_limit = None
    else:
        # Sinon (payg par exemple), on applique le message_limit donné si existant
        if message_limit is not None:
            subscription.message_limit = message_limit

    db.commit()
    db.refresh(subscription)
    return subscription