import os

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine, Session

from dotenv import load_dotenv


# Utilisation des variables d'environnement pour la configuration de la base de données
load_dotenv()  # Charge les variables d'environnement à partir du fichier .env

DATABASE_URL = os.getenv("DATABASE_URL")
Base = declarative_base()

try:
    engine = create_engine(DATABASE_URL, connect_args={})
    # Test de connexion
    with engine.connect() as connection:
        print("Connexion réussie à la base de données.")
except OperationalError as e:
    print(f"Erreur de connexion à la base de données: {e}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    return Session(engine)