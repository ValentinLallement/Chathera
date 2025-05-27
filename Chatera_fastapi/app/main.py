import base64
import io
import requests
import asyncio
import uuid

from fastapi import FastAPI, Depends, HTTPException, status,APIRouter,Body,Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse

from sqlmodel import Session
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from google.auth.transport import requests
from starlette.middleware.sessions import SessionMiddleware
from jose import JWTError, jwt
from contextlib import asynccontextmanager

from . import models, crud, schemas, dependencies, auth
from app.models import Conversation,Bot, User
from app.schemas import CreateBotRequest, UserLogin,PromptRequest, RefreshTokenRequest, UserDeleteRequest, ChangePasswordRequest, PasswordResetRequest, ResetPasswordRequest
from app.auth import verify_token,get_user_from_token, create_password_reset_token
from app.websocket.router import websocket_router
from app.database import get_session
from app.dependencies import get_db
from app.routers import message,auth_google
from app.config import REFRESH_SECRET_KEY, ALGORITHM,config,SECRET_KEY
from app.tasks.scheduler import task_scheduler
from app.utils.permissions import check_bot_limit
from app.utils.email import send_email


from mem0 import Memory

mem0 = Memory.from_config(config)


# --- lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler_task = asyncio.create_task(task_scheduler())
    yield
    scheduler_task.cancel()
    try:
        await scheduler_task
    except asyncio.CancelledError:
        pass

# --- création unique de l'app avec lifespan ---
app = FastAPI(lifespan=lifespan)

# --- configuration de l'app après sa création ---
app.add_middleware(SessionMiddleware, secret_key="une_clef_secrete_pour_session")

app.include_router(websocket_router)
app.include_router(message.router)
app.include_router(auth_google.router)

session = get_session()

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


WEBUI_API_URL = "http://127.0.0.1:7860"

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI is ready!"}

# ----------------- Register -----------------


@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(dependencies.get_db)):
    return crud.create_user(db=db, user=user)


# ----------------- Tokens -----------------

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(
    user: UserLogin,
    db: Session = Depends(dependencies.get_db)
):
    # Cherche par username ou email
    user_from_db = crud.get_user_by_username_or_email(db=db, login=user.login)
    if not user_from_db or not auth.verify_password(user.password, user_from_db.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth.create_access_token(data={"sub": str(user_from_db.id)})
    refresh_token = auth.create_refresh_token(data={"sub": str(user_from_db.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
    

@app.post("/refresh", response_model=schemas.Token)
def refresh_token(
    body: RefreshTokenRequest,  # <== ici on reçoit le JSON
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(body.refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        user = db.query(models.User).get(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        new_access_token = auth.create_access_token(data={"sub": str(user.id)})
        return {
            "access_token": new_access_token,
            "refresh_token": body.refresh_token,
            "token_type": "bearer"
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

# ----------------- User -----------------


@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(dependencies.get_current_user)):
    return current_user

@app.delete("/user/delete")
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

@app.post("/user/change-password")
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

@app.post("/user/request-password-reset")
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


@app.post("/user/reset-password")
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



@app.post("/generate-image/")
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
        response = requests.post(f"{WEBUI_API_URL}/sdapi/v1/txt2img", json=payload)
        response.raise_for_status()
        r = response.json()
        image_data = base64.b64decode(r['images'][0])
        return StreamingResponse(io.BytesIO(image_data), media_type="image/png")

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erreur API Web-UI : {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne : {e}")
    

# ----------------- Bots -----------------




@router.post("/create_bot")
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
    subscription = user.subscription
    if not subscription:
        raise HTTPException(status_code=403, detail="Aucun abonnement trouvé pour l'utilisateur")

    # Vérification de la limite de bots
    existing_bot_count = db.query(Bot).filter(Bot.user_id == user.id).count()
    if not check_bot_limit(subscription, existing_bot_count):
        raise HTTPException(status_code=403, detail="Limite de bots atteinte pour votre abonnement")

    # Création du bot
    bot = Bot(name=request.name, user_id=user.id)
    db.add(bot)
    db.commit()
    db.refresh(bot)

    # Création de la conversation
    conversation = Conversation(user_id=user.id, bot_id=bot.id)
    db.add(conversation)
    db.commit()

    return {"bot_id": bot.id, "conversation_id": conversation.id}


@app.get("/my_bots")
def get_my_bots(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Vérifie le token
    user = get_user_from_token(token, db, credentials_exception)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Récupère les bots créés par l’utilisateur
    bots = db.query(Bot).filter(Bot.user_id == user.id).all()

    return [{"bot_id": bot.id, "name": bot.name} for bot in bots]



# ----------------- Abonnements -----------------

@app.put("/user/subscription", response_model=schemas.SubscriptionUpdate)
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