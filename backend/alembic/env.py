# alembic/env.py
import sqlmodel
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.models import User, Message, Conversation, FutureAction
from app.models import *
import os
import sys

# Ajoute le chemin racine au path (permet d'importer app.*)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Chargement des variables d'environnement depuis .env
from dotenv import load_dotenv
load_dotenv()

# Import des modèles SQLAlchemy
from app.db.base import Base
from app.db import base_model_import  # Force l'import des modèles (User, etc.)
from app.db import base  # Important pour bien charger tous les modèles

# Configuration Alembic
config = context.config
fileConfig(config.config_file_name)

# Chargement de la DATABASE_URL depuis l'environnement (sans l'injecter dans config)
DATABASE_URL = os.getenv("DATABASE_URL")

# Métadonnées utilisées pour les migrations (Base = SQLAlchemy declarative base)
from sqlmodel import SQLModel
target_metadata = SQLModel.metadata

def run_migrations_offline():
    """Exécute les migrations en mode 'offline', sans connexion à la base."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Exécute les migrations en mode 'online', avec connexion à la base."""
    from sqlalchemy import create_engine

    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

# Déclenche le mode de migration approprié
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
