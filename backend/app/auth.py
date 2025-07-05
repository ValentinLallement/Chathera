import os

from uuid import UUID
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional
from dotenv import load_dotenv

from sqlmodel import Session,select
from sqlalchemy.ext.asyncio import AsyncSession


from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status, Request

from app.config import REFRESH_SECRET_KEY, SECRET_KEY, ALGORITHM,ACCESS_TOKEN_EXPIRE_MINUTES
from app.db.models import models
from app.dependencies import get_db


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
async def hash_password(password: str):
    return pwd_context.hash(password)  # Cette fonction hache le mot de passe

async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def create_refresh_token(data: dict, expires_delta: timedelta = timedelta(days=7)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)

async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def get_user_from_token(token: str, db: AsyncSession, credentials_exception: HTTPException):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Convert string user_id to UUID object
    try:
        user_id_uuid = UUID(user_id)  # Convert string to UUID
    except ValueError:
        raise credentials_exception  # Handle invalid UUID format

    # ATTENTION : ici il faut await car AsyncSession.get est async
    user = await db.get(models.User, user_id_uuid)

    if user is None:
        raise credentials_exception
    return user


async def verify_token(request: Request, db: AsyncSession = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="En-tête Authorization manquant ou mal formé")

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token invalide")

        statement = select(models.User).where(models.User.id == user_id)
        result = await db.execute(statement)
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
        
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Token expiré ou invalide")
    
# ----------------- reset password -----------------

async def create_password_reset_token(user_id: int, expires_delta: timedelta = timedelta(minutes=30)) -> str:
    to_encode = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + expires_delta
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def verify_password_reset_token(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=400, detail="Token invalide.")
        return int(user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré.")