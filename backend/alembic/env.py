# alembic/env.py
import sqlmodel
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# 1. Ajouter le chemin parent pour importer app.*
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 2. Charger les variables d'environnement
from dotenv import load_dotenv
load_dotenv()

# 3. Importer la Base et forcer l'import des modèles pour Alembic
from app.db.base import Base   # <-- ta Base SQLAlchemy
from app.db import base_model_import  # supposé importer les modèles

# 4. Charger la config Alembic
config = context.config
fileConfig(config.config_file_name)

# 5. Récupérer l'URL de la base de données
DATABASE_URL = os.getenv("DATABASE_URL")

# 6. Configurer la métadonnée cible pour Alembic
target_metadata = Base.metadata

def run_migrations_offline():
    """Migrations en mode offline"""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Migrations en mode online"""
    from sqlalchemy import create_engine
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
