import base64
import io
import requests
import json

from fastapi import FastAPI, Depends, HTTPException, status,APIRouter,Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse

from sqlmodel import Session
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy.exc import SQLAlchemyError

from google.auth.transport import requests
from starlette.middleware.sessions import SessionMiddleware
from jose import JWTError, jwt
from uuid import UUID
from datetime import datetime, timedelta

from . import models, crud, schemas, dependencies, auth
from app.models import MessageRequest, AutoReplyResponse, Memory, Message, Conversation, FutureAction, User,Bot
from app.schemas import CreateBotRequest, UserLogin, GoogleLogin, PromptRequest, RefreshTokenRequest
from app.auth import verify_token,get_user_from_token
from app.websocket.router import websocket_router
from app.database import get_session
from app.dependencies import get_db
from app.routers import message
from app.routers import auth_google
from app.config import REFRESH_SECRET_KEY, ALGORITHM, GOOGLE_CLIENT_ID






session = get_session()
app = FastAPI()
app.include_router(websocket_router)
app.include_router(message.router)
app.include_router(auth_google.router)
app.add_middleware(SessionMiddleware, secret_key="une_clef_secrete_pour_session")
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
WEBUI_API_URL = "http://127.0.0.1:7860"


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI is ready!"}

@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(dependencies.get_db)):
    return crud.create_user(db=db, user=user)



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



@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(dependencies.get_current_user)):
    return current_user





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
    

@app.post("/create_bot")
def create_bot_and_conversation(request: CreateBotRequest, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = get_user_from_token(token, db, credentials_exception)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Créer un bot avec le user_id
    bot = Bot(name=request.name, user_id=user.id)  # Ajoute user_id ici
    db.add(bot)
    db.commit()
    db.refresh(bot)  # Récupère le bot avec l'ID généré

    # Créer une conversation pour cet utilisateur et ce bot
    conversation = Conversation(user_id=user.id, bot_id=bot.id)
    db.add(conversation)
    db.commit()

    # Retourner l'ID de la conversation et du bot
    return {"bot_id": bot.id, "conversation_id": conversation.id}


@app.get("/my_bots")
def get_my_bots(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Vérifie le token
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = get_user_from_token(token, db, credentials_exception)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Récupère les bots créés par l’utilisateur
    bots = db.query(Bot).filter(Bot.user_id == user.id).all()

    return [{"bot_id": bot.id, "name": bot.name} for bot in bots]