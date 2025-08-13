# app/dependencies.py
import os
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.models import User
from app.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        user = await db.get(User, user_id)

        if user is None:
            raise credentials_exception

        return user

    except JWTError:
        raise credentials_exception
    
async def get_current_user_from_token(token: str, session: AsyncSession) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Comme c'est async, on utilise await
        user = await session.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        return user
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")