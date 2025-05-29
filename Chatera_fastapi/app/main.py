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


from app.websocket.router import websocket_router
from app.database import get_session
from app.dependencies import get_db
from app.routers import message,auth_google,stripe_routes,api_routers
from app.config import REFRESH_SECRET_KEY, ALGORITHM,config,SECRET_KEY
from app.tasks.scheduler import task_scheduler
from app.utils.permissions import check_bot_limit
from app.utils.email import send_email
from app.utils.payg import report_usage
from app.routers.api_routers import api_router
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
app.include_router(stripe_routes.router)
app.include_router(api_router, prefix="/api")

session = get_session()




