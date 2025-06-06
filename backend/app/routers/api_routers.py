import base64
import io
import os
import requests as external_requests  
import asyncio
import uuid
import random
import string

from app.db.models import models
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, Body, Query, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse, JSONResponse

from sqlmodel import Session
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.exc import SQLAlchemyError

from pydantic import BaseModel, EmailStr, Field
from starlette.middleware.sessions import SessionMiddleware
from jose import JWTError, jwt
from contextlib import asynccontextmanager
from datetime import datetime

from google.auth.transport import requests as google_requests

from app import crud, schemas, dependencies, auth
from app.db.models.models import Conversation, Bot, User, Subscription, PlanEnum, SubscriptionStatus, PushSubscription
from app.schemas import (
    CreateBotRequest, UserLogin, PromptRequest, RefreshTokenRequest,
    UserDeleteRequest, ChangePasswordRequest, PasswordResetRequest, ResetPasswordRequest,EmailRequest,
    SubscriptionData

)
from app.auth import verify_token, get_user_from_token, create_password_reset_token
from app.websocket.router import websocket_router
from app.database import get_session
from app.dependencies import get_db
from app.config import REFRESH_SECRET_KEY, ALGORITHM, SECRET_KEY, MEM0_CONFIG ,ACCESS_TOKEN_EXPIRE_MINUTES
from app.tasks.scheduler import task_scheduler
from app.utils.permissions import check_bot_limit
from app.utils.email import send_email, send_email_verification_code
from app.utils.payg import report_usage

from mem0 import Memory

WEBUI_API_URL = "http://127.0.0.1:7860"
mem0 = Memory.from_config(MEM0_CONFIG)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


api_router = APIRouter()

@api_router.get("/")
def read_root():
    return {"message": "Hello, FastAPI is ready!"}

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint for container orchestration"""
    return {"status": "healthy"}

# ----------------- Register -----------------


@api_router.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(dependencies.get_db)):
    return crud.create_user(db=db, user=user)


@api_router.post("/request-email-verification")
def request_email_verification(payload: EmailRequest, db: Session = Depends(dependencies.get_db)):
    email = payload.email

    user = db.query(models.User).filter(models.User.email == email).first()
    if user and user.is_verified:
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé.")

    # Invalider les anciens codes non utilisés
    db.query(models.EmailVerificationCode).filter(
        models.EmailVerificationCode.email == email,
        models.EmailVerificationCode.is_used == False
    ).update({models.EmailVerificationCode.is_used: True})
    db.commit()

    # Générer un nouveau code à 6 chiffres
    code = ''.join(random.choices(string.digits, k=6))

    # Enregistrer le code en base
    db_code = models.EmailVerificationCode(email=email, code=code)
    db.add(db_code)
    db.commit()

    # Envoyer le code par email
    send_email_verification_code(email, code)

    return {"message": "Un nouveau code de vérification a été envoyé."}

@api_router.post("/verify-email-code")
def verify_email_code(payload: schemas.EmailCodeVerification, db: Session = Depends(dependencies.get_db)):
    verification = (
        db.query(models.EmailVerificationCode)
        .filter(
            models.EmailVerificationCode.email == payload.email,
            models.EmailVerificationCode.code == payload.code,
            models.EmailVerificationCode.is_used == False,
            models.EmailVerificationCode.expires_at > datetime.utcnow()
        )
        .order_by(models.EmailVerificationCode.created_at.desc())
        .first()
    )

    if not verification:
        raise HTTPException(status_code=400, detail="Code invalide ou expiré.")

    verification.is_used = True

    # On valide aussi le user
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if user:
        user.is_verified = True
    else:
        raise HTTPException(status_code=400, detail="Utilisateur non trouvé.")

    db.commit()

    return {"message": "Email vérifié avec succès."}
# ----------------- Tokens -----------------

@api_router.post("/token")
def login_for_access_token(
    user: UserLogin,
    db: Session = Depends(dependencies.get_db)
):
    user_from_db = crud.get_user_by_username_or_email(db=db, login=user.login)
    if not user_from_db or not auth.verify_password(user.password, user_from_db.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou mot de passe incorrect")

    access_token = auth.create_access_token(data={"sub": str(user_from_db.id)})
    refresh_token = auth.create_refresh_token(data={"sub": str(user_from_db.id)})

    response = JSONResponse(content={
        "message": "Connexion réussie",
        "access_token": access_token,  # 👉 retourné dans la réponse JSON
        "token_type": "bearer"
    })

    # 🔐 Seul le refresh_token est mis en cookie sécurisé
    if not os.getenv("DEBUG"):
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="Strict",
            max_age=7 * 24 * 60 * 60  # 7 jours
        )
    else:
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,            # << must be False in dev if you're on http://localhost
            samesite="None",          # or "None" if you need truly cross-port/subdomain
            max_age=7 * 24 * 60 * 60,  # 7 days
            path="/",   
        )

    return response
    

@api_router.post("/refresh")
def refresh_token_from_cookie(
    request: Request,
    db: Session = Depends(get_db)
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

        new_access_token = auth.create_access_token(data={"sub": str(user.id)})

        return JSONResponse(content={
            "message": "Token rafraîchi avec succès",
            "access_token": new_access_token,
            "token_type": "bearer"
        })

    except JWTError:
        raise HTTPException(status_code=401, detail="Token de rafraîchissement invalide")
    
@api_router.post("/logout")
def logout():
    response = JSONResponse(content={"message": "Déconnecté"})
    response.delete_cookie(key="refresh_token")
    return response

# ----------------- User -----------------


@api_router.get("/user/me", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(dependencies.get_current_user)):
    return current_user


@api_router.delete("/user/delete")
def delete_account(
    request: UserDeleteRequest,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    user = get_user_from_token(token, db,credentials_exception)

    # Vérifie le mot de passe
    if not auth.verify_password(request.password, user.password):
        raise HTTPException(status_code=403, detail="Mot de passe incorrect.")

    # Supprime l'utilisateur
    db.delete(user)
    db.commit()

    return {"detail": "Compte supprimé avec succès."}

# ----------------- Modify password -----------------

@api_router.post("/user/change-password")
def change_password(
    request: ChangePasswordRequest,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):  

    user = get_user_from_token(token, db,credentials_exception)

    

    # Vérifie l'ancien mot de passe
    if not auth.verify_password(request.old_password, user.password):
        raise HTTPException(status_code=403, detail="Ancien mot de passe incorrect.")

    # Met à jour avec le nouveau mot de passe haché
    user.password = auth.hash_password(request.new_password)
    db.commit()

    return {"detail": "Mot de passe mis à jour avec succès."}
# ----------------- reset password -----------------

@api_router.post("/user/request-password-reset")
def request_password_reset(request: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # Optionnel : ne pas révéler que l’email n'existe pas
        raise HTTPException(status_code=200, detail="Si cet email existe, un lien de réinitialisation a été envoyé.")

    # Générer un token JWT temporaire spécial "reset password"
    reset_token = create_password_reset_token(user.id)

    # Créer le lien de reset à envoyer par email
    reset_link = f"https://Chathera.com/reset-password?token={reset_token}"

    send_email(
        to=user.email,
        subject="Réinitialisation de votre mot de passe",
        body=f"Cliquez ici pour réinitialiser votre mot de passe : {reset_link}"
    )

    return {"detail": f"Un lien de réinitialisation a été envoyé à l'email : {request.email} ."}


@api_router.post("/user/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(request.token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")

    user.password = auth.hash_password(request.new_password)
    db.commit()

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
def create_bot_and_conversation(
    request: CreateBotRequest,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    # Authentification
    user = get_user_from_token(token, db, credentials_exception)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Récupération de l'abonnement
    subscription = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if not subscription:
        raise HTTPException(status_code=403, detail="Aucun abonnement trouvé pour l'utilisateur")

    # Vérification que l'abonnement est actif (hors FREE)
    if subscription.plan != PlanEnum.FREE:
        status = getattr(subscription, "status", None)
        if status != SubscriptionStatus.active:
            raise HTTPException(
                status_code=403,
                detail="Votre abonnement n'est pas actif. Merci de le réactiver pour utiliser le service."
            )

    # Vérification de la limite de bots
    existing_bot_count = db.query(Bot).filter(Bot.user_id == user.id).count()
    if not check_bot_limit(subscription, existing_bot_count):
        raise HTTPException(status_code=403, detail="Limite de bots atteinte pour votre abonnement")

    try:
        # Création du bot
        bot = Bot(name=request.name, user_id=user.id)
        db.add(bot)
        db.commit()
        db.refresh(bot)

        # Création de la conversation associée
        conversation = Conversation(user_id=user.id, bot_id=bot.id)
        db.add(conversation)
        db.commit()

        # Reporting usage Stripe uniquement pour les plans PAYG
        if subscription.plan == PlanEnum.PAYG and subscription.stripe_subscription_item_bots:
            try:
                report_usage(
                    subscription_item_id=subscription.stripe_subscription_item_bots,
                    quantity=1,
                    increment=True
                )
            except Exception as e:
                # Remplacer print par logger dans un vrai projet
                print(f"Erreur lors du report d'usage bots à Stripe : {e}")

        return {"bot_id": bot.id, "conversation_id": conversation.id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur serveur lors de la création du bot : {e}")



@api_router.get("/my_bots")
def get_my_bots(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Vérifie le token
    user = get_user_from_token(token, db, credentials_exception)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Récupère les bots créés par l’utilisateur
    bots = db.query(Bot).filter(Bot.user_id == user.id).all()

    return [{"bot_id": bot.id, "name": bot.name} for bot in bots]



# ----------------- Abonnements -----------------

@api_router.put("/user/subscription", response_model=schemas.SubscriptionUpdate)
async def update_my_subscription(
    subscription_update: schemas.SubscriptionUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    user = get_user_from_token(token, db, credentials_exception)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        updated_subscription = crud.update_user_subscription(
            db=db,
            user_id=user.id,
            new_plan=subscription_update.plan,
            message_limit=subscription_update.message_limit
        )
        return updated_subscription
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
# ----------------- Notification Push -----------------

@api_router.post("/subscribe_push")
async def subscribe_push(subscription: SubscriptionData, user_id: int, db: Session = Depends(get_db)):
    # Vérifier si l'abonnement existe déjà
    existing = db.query(PushSubscription).filter(PushSubscription.endpoint == subscription.endpoint).first()
    if existing:
        return {"message": "Subscription already exists."}
    new_sub = PushSubscription(user_id=user_id, endpoint=subscription.endpoint, keys=subscription.keys)
    db.add(new_sub)
    db.commit()
    return {"message": "Subscription saved."}