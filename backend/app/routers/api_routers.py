import base64
import io
import os
import requests as external_requests  
import asyncio
import uuid
import random
import string
import stripe

from app.db.models import models
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, Body, Query, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse, JSONResponse

from sqlmodel import Session, select
from sqlalchemy.ext.asyncio import AsyncSession

from pydantic import BaseModel, EmailStr, Field
from starlette.middleware.sessions import SessionMiddleware
from jose import JWTError, jwt
from contextlib import asynccontextmanager
from datetime import datetime
from uuid import UUID


from google.auth.transport import requests as google_requests

from app import crud, schemas, dependencies, auth
from app.db.models.models import Conversation, Bot, User, Subscription, PlanEnum, SubscriptionStatus, PushSubscription, UserLegalConsent
from app.schemas import (
    CreateBotRequest, UserLogin, PromptRequest, RefreshTokenRequest,
    UserDeleteRequest, ChangePasswordRequest, PasswordResetRequest, ResetPasswordRequest,EmailRequest,
    SubscriptionData, UserSubscriptionsResponse,SubscriptionInfo,UserLegalConsentBase, UserLegalConsentRead

)
from app.crud import get_or_create_user_consent
from app.auth import verify_token, get_user_from_token, create_password_reset_token
from app.websocket.router import websocket_router
from app.database import get_db
from app.dependencies import get_db
from app.config import REFRESH_SECRET_KEY, ALGORITHM, SECRET_KEY, MEM0_CONFIG ,ACCESS_TOKEN_EXPIRE_MINUTES
from app.tasks.scheduler import task_scheduler
from app.utils.permissions import check_bot_limit
from app.utils.email import send_email, send_email_verification_code
from app.utils.payg import report_usage

from mem0 import Memory

WEBUI_API_URL = "http://127.0.0.1:7860"


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


api_router = APIRouter()

@api_router.get("/")
async def read_root():
    return {"message": "Hello, FastAPI is ready!"}

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint for container orchestration"""
    return {"status": "healthy"}

# ----------------- Register -----------------


@api_router.post("/register", response_model=schemas.User)
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(dependencies.get_db)):
    return crud.create_user(db=db, user=user)



@api_router.post("/request-email-verification")
async def request_email_verification(
    payload: EmailRequest,
    db: AsyncSession = Depends(dependencies.get_db)
):
    email = payload.email

    # await db.execute pour la requête select
    stmt_user = select(models.User).where(models.User.email == email)
    result = await db.execute(stmt_user)
    user = result.scalars().first()

    if user and user.is_verified:
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé.")

    # await db.execute pour la mise à jour (update)
    stmt_update = (
        models.EmailVerificationCode.__table__.update()
        .where(
            (models.EmailVerificationCode.email == email) &
            (models.EmailVerificationCode.is_used == False)
        )
        .values(is_used=True)
    )
    await db.execute(stmt_update)
    await db.commit()

    # Générer un nouveau code à 6 chiffres
    code = ''.join(random.choices(string.digits, k=6))

    # Enregistrer le code en base
    db_code = models.EmailVerificationCode(email=email, code=code)
    db.add(db_code)
    await db.commit()

    # Envoyer le code par email
    await send_email_verification_code(email, code)

    return {"message": "Un nouveau code de vérification a été envoyé."}


@api_router.post("/verify-email-code")
async def verify_email_code(
    payload: schemas.EmailCodeVerification,
    db: AsyncSession = Depends(dependencies.get_db)
):
    stmt_verif = (
        select(models.EmailVerificationCode)
        .where(
            (models.EmailVerificationCode.email == payload.email) &
            (models.EmailVerificationCode.code == payload.code) &
            (models.EmailVerificationCode.is_used == False) &
            (models.EmailVerificationCode.expires_at > datetime.utcnow())
        )
        .order_by(models.EmailVerificationCode.created_at.desc())
    )

    result_verif = await db.execute(stmt_verif)
    verification = result_verif.scalars().first()  # Note: first() n'est pas async

    if not verification:
        raise HTTPException(status_code=400, detail="Code invalide ou expiré.")

    verification.is_used = True

    # Recherche utilisateur
    stmt_user = select(models.User).where(models.User.email == payload.email)
    result_user = await db.execute(stmt_user)
    user = result_user.scalars().first()

    if not user:
        raise HTTPException(status_code=400, detail="Utilisateur non trouvé.")

    user.is_verified = True

    await db.commit()

    return {"message": "Email vérifié avec succès."}
# ----------------- Tokens -----------------

@api_router.post("/token")
async def login_for_access_token(
    user: UserLogin,
    db: AsyncSession = Depends(dependencies.get_db)
):
    user_from_db = await crud.get_user_by_username_or_email(db=db, login=user.login)
    if not user_from_db or not await auth.verify_password(user.password, user_from_db.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou mot de passe incorrect")

    access_token = await auth.create_access_token(data={"sub": str(user_from_db.id)})
    refresh_token = await auth.create_refresh_token(data={"sub": str(user_from_db.id)})

    response = JSONResponse(content={
        "message": "Connexion réussie",
        "access_token": access_token,
        "token_type": "bearer"
    })

    # Set refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=7 * 24 * 60 * 60,  # 7 days
        path="/"  # Match the proxy path
    )

    return response
    

@api_router.post("/refresh")
async def refresh_token_from_cookie(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token manquant")

    try:
        payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token invalide")

        # Convertir user_id (chaîne) en uuid.UUID
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        user = db.get(models.User, user_uuid)
        if not user:
            raise HTTPException(status_code=401, detail="Utilisateur non trouvé")

        new_access_token = await auth.create_access_token(data={"sub": str(user.id)})

        return JSONResponse(content={
            "message": "Token rafraîchi avec succès",
            "access_token": new_access_token,
            "token_type": "bearer"
        })

    except JWTError:
        raise HTTPException(status_code=401, detail="Token de rafraîchissement invalide")
    
@api_router.post("/logout")
async def logout():
    response = JSONResponse(content={"message": "Déconnecté"})
    response.delete_cookie(key="refresh_token")
    return response

# ----------------- User -----------------


@api_router.get("/user/me", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(dependencies.get_current_user)):
    return current_user


@api_router.delete("/user/delete")
async def delete_account(
    request: UserDeleteRequest,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    user = await get_user_from_token(token, db,credentials_exception)

    # Vérifie le mot de passe
    if not await auth.verify_password(request.password, user.password):
        raise HTTPException(status_code=403, detail="Mot de passe incorrect.")

    # Supprime l'utilisateur
    db.delete(user)
    await db.commit()

    return {"detail": "Compte supprimé avec succès."}

# ----------------- Modify password -----------------

@api_router.post("/user/change-password")
async def change_password(
    request: ChangePasswordRequest,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):  

    user = await get_user_from_token(token, db,credentials_exception)

    

    # Vérifie l'ancien mot de passe
    if not await auth.verify_password(request.old_password, user.password):
        raise HTTPException(status_code=403, detail="Ancien mot de passe incorrect.")

    # Met à jour avec le nouveau mot de passe haché
    user.password = await auth.hash_password(request.new_password)
    await db.commit()

    return {"detail": "Mot de passe mis à jour avec succès."}
# ----------------- reset password -----------------

@api_router.post("/user/request-password-reset")
async def request_password_reset(request: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == request.email)
    user = await db.execute(stmt).scalars().first()

    # Toujours répondre la même chose pour ne pas révéler l'existence de l'email
    if not user:
        return {"detail": "Si cet email existe, un lien de réinitialisation a été envoyé."}

    reset_token = await create_password_reset_token(user.id)
    reset_link = f"https://Chathera.com/reset-password?token={reset_token}"

    await send_email(
        to=user.email,
        subject="Réinitialisation de votre mot de passe",
        body=f"Cliquez ici pour réinitialiser votre mot de passe : {reset_link}"
    )

    return {"detail": f"Un lien de réinitialisation a été envoyé à l'email : {request.email}."}


@api_router.post("/user/reset-password")
async def reset_password(request: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(request.token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token invalide ou expiré.")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré.")

    stmt = select(User).where(User.id == user_id)
    user = await db.execute(stmt).scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")

    user.password = await auth.hash_password(request.new_password)
    await db.commit()

    return {"detail": "Mot de passe réinitialisé avec succès."}

# ----------------- Images -----------------



@api_router.post("/generate-image/")
async def generate_image(data: PromptRequest, token: str = Depends(verify_token)):
    """
    Génère une image protégée par token via l'API Stable Diffusion Web-UI.
    """
    payload = {
        "prompt": data.prompt,
        "steps": 30,
        "sampler_index": "Euler a",
        "cfg_scale": 7.5,
        "width": 512,
        "height": 512,
    }

    try:
        response = external_requests.post(f"{WEBUI_API_URL}/sdapi/v1/txt2img", json=payload)
        response.raise_for_status()
        r = response.json()
        image_data = base64.b64decode(r['images'][0])
        return StreamingResponse(io.BytesIO(image_data), media_type="image/png")

    except external_requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erreur API Web-UI : {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne : {e}")
    

# ----------------- Bots -----------------


@api_router.post("/create_bot")
async def create_bot_and_conversation(
    request: CreateBotRequest,
    token: str = Depends(dependencies.oauth2_scheme),
    db: AsyncSession = Depends(dependencies.get_db)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Impossible de valider les identifiants.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Récupération utilisateur via token
    user = await get_user_from_token(token, db, credentials_exception)

    # Vérifie que l'utilisateur a un abonnement
    result = await db.execute(
        select(models.Subscription).where(models.Subscription.user_id == user.id)
    )
    subscription = result.scalars().first()

    if not subscription:
        raise HTTPException(status_code=403, detail="Aucun abonnement trouvé pour l'utilisateur")

    # Si plan ≠ FREE, abonnement doit être actif
    if subscription.plan != PlanEnum.FREE and subscription.status != SubscriptionStatus.active:
        raise HTTPException(
            status_code=403,
            detail="Votre abonnement n'est pas actif. Merci de le réactiver pour utiliser le service."
        )

    # Compter les bots existants
    result = await db.execute(
        select(models.Bot).where(models.Bot.user_id == user.id)
    )
    existing_bots = result.scalars().all()
    existing_bot_count = len(existing_bots)

    # Vérifier la limite
    if not check_bot_limit(subscription, existing_bot_count):
        raise HTTPException(status_code=403, detail="Limite de bots atteinte pour votre abonnement")

    # Création du bot et conversation
    try:
        new_bot = models.Bot(
            name=request.name,
            user_id=user.id,
            gender=request.gender,
            personality=request.personality
        )
        db.add(new_bot)
        await db.commit()
        await db.refresh(new_bot)

        new_conversation = models.Conversation(
            user_id=user.id,
            bot_id=new_bot.id
        )
        db.add(new_conversation)
        await db.commit()
        await db.refresh(new_conversation)

        # Report d’usage Stripe (facultatif)
        if subscription.plan == PlanEnum.PAYG and subscription.stripe_subscription_item_bots:
            try:
                report_usage(
                    subscription_item_id=subscription.stripe_subscription_item_bots,
                    quantity=1,
                    increment=True
                )
            except Exception as e:
                print(f"Erreur lors du report d'usage bots à Stripe : {e}")

        return {
            "bot_id": new_bot.id,
            "conversation_id": new_conversation.id
        }

    except Exception as e:
        await db.rollback()
        print(f"Erreur serveur lors de la création du bot : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur serveur lors de la création du bot.")


@api_router.delete("/delete_bot/{bot_id}")
async def delete_bot(
    bot_id: UUID,
    token: str = Depends(dependencies.oauth2_scheme),
    db: AsyncSession = Depends(dependencies.get_db)
):
    user = await get_user_from_token(token, db, credentials_exception)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Attention à await db.execute et récupérer le résultat avant .scalars().first()
    stmt_bot = select(Bot).where(Bot.id == bot_id, Bot.user_id == user.id)
    result_bot = await db.execute(stmt_bot)
    bot = result_bot.scalars().first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot non trouvé ou pas les droits")

    stmt_sub = select(models.Subscription).where(models.Subscription.user_id == user.id)
    result_sub = await db.execute(stmt_sub)
    subscription = result_sub.scalars().first()
    if not subscription:
        raise HTTPException(status_code=403, detail="Aucun abonnement trouvé")

    try:
        # Supprimer les conversations liées
        stmt_conv = select(Conversation).where(Conversation.bot_id == bot.id)
        result_conv = await db.execute(stmt_conv)
        conversations = result_conv.scalars().all()

        for conv in conversations:
            await db.delete(conv)  # La méthode delete() est asynchrone en AsyncSession

        await db.commit()

        await db.delete(bot)
        await db.commit()

        if subscription.plan == PlanEnum.PAYG and subscription.stripe_subscription_item_bots:
            try:
                report_usage(subscription_item_id=subscription.stripe_subscription_item_bots, quantity=1, increment=False)
            except Exception as e:
                print(f"Erreur report Stripe suppression bot : {e}")

        return {"detail": f"Bot {bot.name} supprimé avec succès"}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression : {e}")


@api_router.get("/my_bots")
async def get_my_bots(token: str = Depends(dependencies.oauth2_scheme), db: AsyncSession = Depends(dependencies.get_db)):
    user = await get_user_from_token(token, db, credentials_exception)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    stmt_bots = select(Bot).where(Bot.user_id == user.id)
    result = await db.execute(stmt_bots)         
    bots = result.scalars().all()

    return [{"bot_id": bot.id, "name": bot.name, "gender": bot.gender, "avatar_url": bot.avatar_url} for bot in bots]



# ----------------- Abonnements -----------------

@api_router.put("/user/subscription/update", response_model=schemas.SubscriptionUpdate)
async def update_my_subscription(
    subscription_update: schemas.SubscriptionUpdate,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    user = await get_user_from_token(token, db, credentials_exception)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = subscription_update.dict(exclude_unset=True)

    try:
        updated_subscription = crud.update_user_subscription(
            db=db,
            user_id=user.id,
            new_plan=update_data.get("plan"),
            message_limit=update_data.get("message_limit"),
            message_limit_provided="message_limit" in update_data
        )
        return updated_subscription
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    

@api_router.get("/user/subscription/infos", response_model=UserSubscriptionsResponse)
async def get_user_subscription(
    token: str = Depends(dependencies.oauth2_scheme),
    db: AsyncSession = Depends(dependencies.get_db)
):
    user = await get_user_from_token(token, db, credentials_exception)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    stmt_sub = select(models.Subscription).where(models.Subscription.user_id == user.id)
    result = await db.execute(stmt_sub)
    subscription = result.scalars().first()

    if not subscription:
        return UserSubscriptionsResponse(subscriptions=None)

    # Base locale
    subs_info = SubscriptionInfo(
        id=subscription.id,
        user_id=user.id,
        plan=subscription.plan,
        status=subscription.status,
        message_count=subscription.message_count,
        free_message_count=subscription.free_message_count,
        message_limit=subscription.message_limit,
    )

    # 🔁 Ajout des données Stripe
    if subscription.stripe_subscription_id:
        try:
            stripe_sub = stripe.Subscription.retrieve(
                subscription.stripe_subscription_id,
                expand=["items.data.price"]
            )
            import json
            print(f"[SubscriptionInfo] Récupération des infos Stripe pour l'abonnement {subscription.id} ({subscription.stripe_subscription_id})")
            print(json.dumps(stripe_sub, indent=2))  # debug uniquement

            # Récupérer le premier item d'abonnement
            item = stripe_sub["items"]["data"][0] if stripe_sub.get("items") and stripe_sub["items"]["data"] else None

            if item:
                subs_info.stripe_current_period_start = datetime.fromtimestamp(
                    item.get("current_period_start")) if item.get("current_period_start") else None
                subs_info.stripe_current_period_end = datetime.fromtimestamp(
                    item.get("current_period_end")) if item.get("current_period_end") else None
            else:
                subs_info.stripe_current_period_start = None
                subs_info.stripe_current_period_end = None

            subs_info.stripe_cancel_at_period_end = stripe_sub.get("cancel_at_period_end")

            price = item.get("price", {}) if item else {}
            subs_info.stripe_plan_amount_eur = (price.get("unit_amount", 0) / 100) if price.get("unit_amount") else None
            subs_info.stripe_currency = price.get("currency")

        except Exception as e:
            print(f"[SubscriptionInfo] Erreur Stripe : {e}")
    return UserSubscriptionsResponse(subscriptions=subs_info)


# ------------------------- Consent -------------------------

@api_router.post("/legal/accept", response_model=UserLegalConsentRead)
async def accept_legal_consent(
    consent_data: UserLegalConsentBase,
    token: str = Depends(dependencies.oauth2_scheme),
    db: AsyncSession = Depends(dependencies.get_db)
):
    user = await get_user_from_token(token, db, credentials_exception)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    consent = await get_or_create_user_consent(db, user.id)

    now = datetime.utcnow()
    # Pour chaque champ accepté à True, on met à jour la date correspondante
    if consent_data.accepted_terms is True:
        consent.accepted_terms = True
        consent.accepted_terms_at = now

    if consent_data.accepted_privacy is True:
        consent.accepted_privacy = True
        consent.accepted_privacy_at = now

    if consent_data.accepted_cookies is True:
        consent.accepted_cookies = True
        consent.accepted_cookies_at = now

    await db.commit()
    await db.refresh(consent)
    return consent


@api_router.put("/legal/update", response_model=UserLegalConsentRead)
async def update_legal_consent(
    update_data: UserLegalConsentBase,
    token: str = Depends(dependencies.oauth2_scheme),
    db: AsyncSession = Depends(dependencies.get_db)
):
    user = await get_user_from_token(token, db, credentials_exception)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    consent = await get_or_create_user_consent(db, user.id)
    now = datetime.utcnow()

    # Modifie chaque champ, met à jour la date ou supprime la date si False
    if update_data.accepted_terms is not None:
        consent.accepted_terms = update_data.accepted_terms
        consent.accepted_terms_at = now if update_data.accepted_terms else None

    if update_data.accepted_privacy is not None:
        consent.accepted_privacy = update_data.accepted_privacy
        consent.accepted_privacy_at = now if update_data.accepted_privacy else None

    if update_data.accepted_cookies is not None:
        consent.accepted_cookies = update_data.accepted_cookies
        consent.accepted_cookies_at = now if update_data.accepted_cookies else None

    await db.commit()
    await db.refresh(consent)
    return consent