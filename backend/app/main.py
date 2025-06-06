import warnings

# ignore les avertissements de dépréciation venus de FAISS
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    module="faiss.loader"
)

# ignore les messages du type "builtin type SwigPyPacked has no __module__"
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    message=r"builtin type .* has no __module__"
)

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


import base64
import io
import requests
import asyncio
import uuid
import os
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, Body, Query, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

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
from app.config import REFRESH_SECRET_KEY, ALGORITHM, SECRET_KEY, MEM0_CONFIG
from app.tasks.scheduler import task_scheduler
from app.utils.permissions import check_bot_limit
from app.utils.email import send_email
from app.utils.payg import report_usage
from app.routers.api_routers import api_router
from mem0 import Memory

mem0 = Memory.from_config(MEM0_CONFIG)


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

app.add_middleware(SessionMiddleware, secret_key="une_clef_secrete_pour_session")

origins = [
    "http://localhost:5173",  # front-end origin
]

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Use the specific origins instead of "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(websocket_router)
app.include_router(message.router)
app.include_router(auth_google.router)
app.include_router(stripe_routes.router)
app.include_router(api_router, prefix="/api")



######################
#        Front       #
######################


"""# Serve static files from frontend build 
app.mount("/static", StaticFiles(directory="../frontend/dist/static"), name="static")

BASE_DIR = Path(__file__).parent
favicon_path = BASE_DIR / 'favicon.webp'

@app.get('/favicon.webp', include_in_schema=False)
async def favicon():
    return FileResponse(str(favicon_path))

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    return FileResponse("../frontend/dist/index.html")

"""


