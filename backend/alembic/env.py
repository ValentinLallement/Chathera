import os
import sys
from logging.config import fileConfig
from configparser import ConfigParser

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
from alembic import context
from sqlmodel import SQLModel

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Ajouter le dossier racine au path pour l'import des modules `app`
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(BASE_DIR)

# Import des modèles pour que Alembic les détecte
from app.db.models.models import (
    User,
    Message,
    Conversation,
    Bot,
    FutureAction,
    MemoryEntry,
    Subscription,
    UsageLog,
    MonthlyUsage,
    EmailVerificationCode
)

# Configuration Alembic
config = context.config

# Récupérer l'URL de la base de données
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise EnvironmentError("DATABASE_URL non défini dans le fichier .env")

# Corriger le problème d'interpolation avec %
if config.config_file_name:
    parser = ConfigParser(interpolation=None)
    parser.read(config.config_file_name)
    parser.set(config.config_ini_section, "sqlalchemy.url", database_url)
    config.file_config = parser

# Configuration du logging
fileConfig(config.config_file_name)

# Définir les métadonnées des modèles pour Alembic
target_metadata = SQLModel.metadata


def run_migrations_offline():
    """Exécute les migrations sans se connecter à la base de données."""
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Exécute les migrations en se connectant à la base de données."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# Déclenchement selon le mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
