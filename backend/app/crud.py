import re
import unicodedata
import uuid
import random
import string

from .db.models import models
from sqlmodel import Session, select
from sqlalchemy.ext.asyncio import AsyncSession

from passlib.context import CryptContext
from uuid import UUID
from datetime import datetime
from typing import Optional, Union

from fastapi import HTTPException

from . import schemas,auth
from app.db.models.models import Conversation, Message, FutureAction, Subscription, UserLegalConsent
from app.utils.payg import PlanEnum
from app.utils.email import send_email_verification_code,send_account_created_email
from app.utils.permissions import MESSAGE_LIMITS



#----------------------  User  --------------------------------------------------

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user_from_draft(db: AsyncSession, email: str) -> models.User:
    # Vérifier que le code email a été validé
    stmt_code = (
        select(models.EmailVerificationCode)
        .where(
            (models.EmailVerificationCode.email == email) &
            (models.EmailVerificationCode.is_used == True) &
            (models.EmailVerificationCode.expires_at > datetime.utcnow())
        )
        .order_by(models.EmailVerificationCode.created_at.desc())
    )
    result_code = await db.execute(stmt_code)
    valid_code = result_code.scalars().first()
    if valid_code is None:
        raise HTTPException(status_code=400, detail="L'email je te le fous dabs le cul")

    # Récupérer le brouillon d'inscription
    stmt_draft = select(models.UserDraft).where(models.UserDraft.email == email)
    result_draft = await db.execute(stmt_draft)
    draft = result_draft.scalars().first()
    if not draft:
        raise HTTPException(status_code=404, detail="Brouillon introuvable.")

    # Vérification redondante : username / email pas déjà utilisés
    stmt_user = select(models.User).where(models.User.email == email)
    if (await db.execute(stmt_user)).scalars().first():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    stmt_username = select(models.User).where(models.User.username == draft.username)
    if (await db.execute(stmt_username)).scalars().first():
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris")

    # Création de l'utilisateur
    user = models.User(
        email=draft.email,
        username=draft.username,
        name=draft.name,
        password=draft.password,
        is_verified=True
    )
    db.add(user)
    await db.flush()

    # Souscription gratuite
    subscription = models.Subscription(
        user_id=user.id,
        plan=models.PlanEnum.FREE,
        status="active"
    )
    db.add(subscription)

    # Supprimer le brouillon
    await db.delete(draft)
    await db.commit()
    await db.refresh(user)

    # Email de bienvenue
    try:
        await send_account_created_email(to_email=user.email, user_first_name=user.name or user.username)
    except Exception as e:
        print(f"[create_user_from_draft] Erreur lors de l'envoi du mail de bienvenue : {e}")

    return user



async def get_user_by_username(db: AsyncSession, username: str):
    stmt = select(models.User).where(models.User.username == username)
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_user_by_username_or_email(db: AsyncSession, login: str):
    stmt = select(models.User).where(
        (models.User.username == login) | (models.User.email == login)
    )
    result = await db.execute(stmt)
    return result.scalars().first()


async def generate_unique_username(db: AsyncSession, base_username: str) -> str:
    username = base_username
    i = 1
    while True:
        stmt = select(models.User).where(models.User.username == username)
        result = await db.execute(stmt)
        if not result.scalars().first():
            break
        username = f"{base_username}{i}"
        i += 1
    return username


async def normalize_username(name: str) -> str:
    name = unicodedata.normalize('NFD', name).encode('ascii', 'ignore').decode('utf-8')
    name = re.sub(r'\s+', '_', name).lower()
    name = re.sub(r'[^\w_]', '', name)
    return name


async def create_or_update_user_google(db: AsyncSession, email: str, name: Optional[str], google_sub: str, picture: Optional[str] = None):
    stmt_google_sub = select(models.User).where(models.User.google_sub == google_sub)
    result = await db.execute(stmt_google_sub)
    user = result.scalars().first()
    if user:
        updated = False
        if name and user.name != name:
            user.name = name
            updated = True
        if picture and user.profile_picture != picture:
            user.profile_picture = picture
            updated = True
        if updated:
            await db.commit()
            await db.refresh(user)
        return user

    stmt_email = select(models.User).where(models.User.email == email)
    result = await db.execute(stmt_email)
    user = result.scalars().first()
    if user:
        updated = False
        if user.google_sub != google_sub:
            user.google_sub = google_sub
            updated = True
        if name and user.name != name:
            user.name = name
            updated = True
        if picture and user.profile_picture != picture:
            user.profile_picture = picture
            updated = True
        if updated:
            await db.commit()
            await db.refresh(user)
        return user

    base_username = await normalize_username(name or email.split('@')[0])
    username = await generate_unique_username(db, base_username)

    new_user = models.User(
        email=email,
        name=name,
        google_sub=google_sub,
        password=None,
        username=username,
        profile_picture=picture 
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    free_subscription = models.Subscription(
        user_id=new_user.id,
        plan=models.PlanEnum.FREE,
        status="active"
    )
    db.add(free_subscription)
    await db.commit()
    await db.refresh(free_subscription)

    new_user.subscriptions.append(free_subscription)

    return new_user


async def get_user_by_google_sub(db: AsyncSession, google_sub: str):
    stmt = select(models.User).where(models.User.google_sub == google_sub)
    result = await db.execute(stmt)
    return result.scalars().first()

#-----------------------------  Conversation  -------------------------------------------



# Conversation
async def create_conversation(session: Session, user_id: UUID) -> Conversation:
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


async def get_conversation_by_id(session: Session, conversation_id: UUID) -> Conversation | None:
    return session.get(Conversation, conversation_id)


# Message
async def create_message(session: Session, user_id: UUID, conversation_id: UUID, content: str) -> Message:
    message = Message(user_id=user_id, conversation_id=conversation_id, content=content)
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


# FutureAction
async def create_future_action(
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


async def get_messages_by_user(db: AsyncSession, user_id: UUID) -> list[Message]:
    stmt = (
        select(Message)
        .where(Message.user_id == user_id)
        .order_by(Message.created_at)  # Optionnel : tri par date
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def update_user_subscription(
    db: AsyncSession,
    user_id: UUID,
    new_plan: Optional[Union[str, PlanEnum]] = None,
    message_limit: Optional[int] = None,
    message_limit_provided: bool = False
):
    stmt = select(Subscription).where(Subscription.user_id == user_id)
    result = await db.exe(stmt)
    subscription = result.scalars().first()

    if not subscription:
        subscription = Subscription(
            user_id=user_id,
            plan=PlanEnum.FREE,
            message_limit=None,
            message_count=0,
            start_date=datetime.utcnow(),
            last_reset=datetime.utcnow().date()
        )
        db.add(subscription)
        await db.flush()  # flush async

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

        if not message_limit_provided:
            subscription.message_limit = MESSAGE_LIMITS.get(new_plan, None)

    if message_limit_provided:
        subscription.message_limit = message_limit

    await db.commit()
    await db.refresh(subscription)
    return subscription

# ----------------------------- Consent ---------------------------------------

async def get_or_create_user_consent(db: AsyncSession, user_id: str) -> UserLegalConsent:
    result = await db.execute(
        select(UserLegalConsent).where(UserLegalConsent.user_id == user_id)
    )
    consent = result.scalar_one_or_none()

    if not consent:
        consent = UserLegalConsent(user_id=user_id)
        db.add(consent)
        await db.commit()
        await db.refresh(consent)

    return consent







