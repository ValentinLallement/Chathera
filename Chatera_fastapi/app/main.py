import base64
import io
import requests
import json

from uuid import UUID
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, status,APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse

from sqlmodel import Session
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from . import models, crud, schemas, dependencies, auth

from app.models import MessageRequest, AutoReplyResponse, Memory, Message, Conversation, FutureAction, User,Bot
from app.schemas import CreateBotRequest
from app.auth import verify_token,get_user_from_token
from app.websocket.router import websocket_router
from app.utils.auto_reply import build_prompt, get_auto_reply_from_deepseek
from app.database import get_session
from app.dependencies import get_db
from app.routers import message




session = get_session()
app = FastAPI()
app.include_router(websocket_router)
app.include_router(message.router)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
WEBUI_API_URL = "http://127.0.0.1:7860"


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI is ready!"}

@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(dependencies.get_db)):
    return crud.create_user(db=db, user=user)

class UserLogin(BaseModel):
    username: str
    password: str

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(
    user: UserLogin,  # Changer ici pour accepter un corps JSON
    db: Session = Depends(dependencies.get_db)
):
    # Vérification des informations d'identification
    user_from_db = crud.get_user_by_username(db=db, username=user.username)
    if not user_from_db or not auth.verify_password(user.password, user_from_db.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user_from_db.username})
    return {"access_token": access_token, "token_type": "bearer"}



@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(dependencies.get_current_user)):
    return current_user




class PromptRequest(BaseModel):
    prompt: str

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