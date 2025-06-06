import pytest
from fastapi.testclient import TestClient
import sys
import os

# Assure le bon chemin d'import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.dependencies import get_db
from tests.test_database import create_test_db, drop_test_db, get_test_session, engine_test

@pytest.fixture(scope="module")
def client():
    create_test_db()
    def override_get_db():
        session = get_test_session()
        try:
            yield session
        finally:
            session.close()  # Explicitly close the session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()  # Clear overrides
    engine_test.dispose()  # Ensure engine connections are closed
    drop_test_db()