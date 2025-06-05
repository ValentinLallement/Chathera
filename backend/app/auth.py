import os

from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional
from dotenv import load_dotenv

from sqlalchemy.orm import Session

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status, Request

from app.config import REFRESH_SECRET_KEY, SECRET_KEY, ALGORITHM,ACCESS_TOKEN_EXPIRE_MINUTES
from . import models
from .database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
def hash_password(password: str):
    return pwd_context.hash(password)  # Cette fonction hache le mot de passe

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta = timedelta(days=7)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user_from_token(token: str, db: Session, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Suppression de int() car user_id est un UUID string
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if user is None:
        raise credentials_exception
    return user

# Fonction pour vérifier le token
def verify_token(request: Request, db: Session = Depends(get_db)):
    # Récupère le token depuis le cookie "access_token"
    token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(status_code=401, detail="Token manquant dans les cookies")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token invalide")

        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
        
        return user  # ✅ l'utilisateur est authentifié
    except JWTError:
        raise HTTPException(status_code=401, detail="Token expiré ou invalide")
    
# ----------------- reset password -----------------

def create_password_reset_token(user_id: int, expires_delta: timedelta = timedelta(minutes=30)) -> str:
    to_encode = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + expires_delta
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_password_reset_token(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=400, detail="Token invalide.")
        return int(user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré.")