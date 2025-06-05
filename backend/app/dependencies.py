import os

from jose import jwt, JWTError

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status,WebSocket, Request
from fastapi.security import OAuth2PasswordBearer


from app.models import User
from app.database import get_session
from . import models, schemas, auth
from .database import SessionLocal

from dotenv import load_dotenv
load_dotenv()

session = get_session()

SECRET_KEY = (os.getenv("SECRET_KEY"))  # Utilisez os.getenv pour obtenir la valeur de l'environnement
ALGORITHM = (os.getenv("ALGORITHM"))  # Utilisez os.getenv pour obtenir la valeur de l'environnement

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(request:Request, db: Session = Depends(get_db)):
    
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Token manquant dans les cookies")

    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return auth.get_user_from_token(token, db, credentials_exception)

def get_current_user_from_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = session.get(User, user_id)
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")
    

async def get_user_from_websocket(websocket: WebSocket) -> User:
    token = websocket.query_params.get("token")
    print(">> TOKEN RECU:", token)

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        print(">> PAYLOAD:", payload)
        print(">> USERNAME extrait:", username)

        if username is None:
            raise HTTPException(status_code=403, detail="Invalid token")
    except JWTError as e:
        print(">> JWT Error:", e)
        raise HTTPException(status_code=403, detail="Could not validate credentials")

    # MANUAL SESSION HERE
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == username).first()

        print(">> USER en base:", user)
    finally:
        db.close()

    if user is None:
        raise HTTPException(status_code=403, detail="User not found")

    return user