import os
import time
import gc
from sqlmodel import SQLModel, create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import tempfile

from app.db.models.models import *  # Assure-toi que tous tes modèles sont bien importés ici

# Création d’un fichier temporaire SQLite pour la session de test
temp_db_file = os.path.join(tempfile.gettempdir(), "test_chathera.db")
TEST_DATABASE_URL = f"sqlite:///{temp_db_file}"

# Création de l'engine SQLAlchemy pour la base de test
engine_test = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Session locale pour la base de test
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_test,
)

def create_test_db() -> None:
    """
    Crée toutes les tables pour la base de test.
    """
    SQLModel.metadata.create_all(bind=engine_test)

def drop_test_db() -> None:
    """
    Supprime la base temporaire de test avec réessais en cas de verrouillage.
    """
    gc.collect()  # Force la libération des connexions
    engine_test.dispose()  # Close all connections in the engine's pool
    if os.path.exists(temp_db_file):
        max_attempts = 5
        attempt = 1
        while attempt <= max_attempts:
            try:
                os.remove(temp_db_file)
                print(f"Test database {temp_db_file} deleted successfully.")
                return
            except PermissionError as e:
                print(f"Attempt {attempt}/{max_attempts} failed to delete {temp_db_file}: {e}")
                time.sleep(1)  # Wait before retrying
                attempt += 1
        print(f"⚠️ Impossible de supprimer test DB {temp_db_file} after {max_attempts} attempts. Réessaye après fermeture des processus.")

@contextmanager
def get_test_session():
    """
    Fournit une session DB pour les tests avec fermeture propre.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()