# app/database.py
import logging

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

import os
from dotenv import load_dotenv
from typing import AsyncGenerator




load_dotenv()


logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL.startswith("postgresql+asyncpg://"):
    raise ValueError("DATABASE_URL doit commencer par 'postgresql+asyncpg://'")

#Création de l'engine async avec SQLAlchemy
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

#Création du sessionmaker
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

#Dépendance FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

#Création des tables
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
