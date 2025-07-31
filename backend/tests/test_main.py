import pytest
from fastapi.testclient import TestClient
import sys
import os
from uuid import uuid4
from sqlalchemy import select
from datetime import datetime, timezone
from app.db.models.models import EmailVerificationCode, User, Subscription, PlanEnum, SubscriptionStatus

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.main import app
from app.dependencies import get_db
from tests.test_database import create_test_db, drop_test_db, get_test_session

# Define fixtures for unique test data
@pytest.fixture(scope="function")
def email_test():
    return f"user_{str(uuid4())}@test.com"

@pytest.fixture(scope="function")
def unique_username():
    return "testuser_" + str(uuid4())[:8]

@pytest.fixture(scope="function")
def password_test():
    return "strongpassword123"

@pytest.fixture(scope="module")
def client():
    create_test_db()
    def override_get_db():
        with get_test_session() as session:
            yield session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    drop_test_db()

async def test_read_root(client):
    response = client.get("/api/")
    print(f"Read root status: {response.status_code}, response: {response.text}")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, FastAPI is ready!"}

async def test_health_check(client):
    response = client.get("/api/health")
    print(f"Health check status: {response.status_code}, response: {response.text}")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

async def test_register_user(client, email_test, unique_username, password_test):
    user_data = {
        "username": unique_username,
        "email": email_test,
        "password": password_test,
        "name": "TestUser",
    }
    response = client.post("/api/register", json=user_data)
    print(f"Register status: {response.status_code}, response: {response.text}")
    assert response.status_code == 200, f"Register failed: status {response.status_code}, response: {response.text}"
    response_data = response.json()
    assert response_data is not None, "Response JSON is empty or invalid"
    assert "email" in response_data, "Email key missing in response"
    assert response_data["email"] == user_data["email"], "Returned email does not match"
    assert "id" in response_data, "ID not returned"
    print(f"Registered user ID: {response_data['id']}, type: {type(response_data['id'])}")

async def test_email_verification_flow(client, email_test, unique_username, password_test):
    # Register a user first
    user_data = {
        "username": unique_username,
        "email": email_test,
        "password": password_test,
        "name": "TestUser",
    }
    response = client.post("/api/register", json=user_data)
    print(f"Register for email verification status: {response.status_code}, response: {response.text}")
    assert response.status_code == 200

    # Request email verification
    response = client.post("/api/request-email-verification", json={"email": email_test})
    print(f"Request email verification status: {response.status_code}, response: {response.text}")
    assert response.status_code == 200

    # Get verification code
    with get_test_session() as db:
        stmt = select(EmailVerificationCode).where(EmailVerificationCode.email == email_test).order_by(EmailVerificationCode.created_at.desc())
        verification = await db.execute(stmt).scalars().scalars().first()
        assert verification is not None, "Verification code not found"
        verification_code = str(verification.code)
        print(f"Verification code: {verification_code}, type: {type(verification_code)}")

    # Verify email code
    response = client.post("/api/verify-email-code", json={"email": email_test, "code": verification_code})
    print(f"Verify email code status: {response.status_code}, response: {response.text}")
    assert response.status_code == 200, f"Verify email failed: {response.text}"

async def test_login_and_refresh_token(client, email_test, unique_username, password_test):
    # Register and verify user
    user_data = {
        "username": unique_username,
        "email": email_test,
        "password": password_test,
        "name": "TestUser",
    }
    response = client.post("/api/register", json=user_data)
    print(f"Register for login test: {response.status_code}, response: {response.text}")
    assert response.status_code == 200
    response_data = response.json()
    user_id = response_data["id"]
    print(f"Registered user ID: {user_id}, type: {type(user_id)}")

    # Verify email
    response = client.post("/api/request-email-verification", json={"email": email_test})
    print(f"Request email verification for login: {response.status_code}, response: {response.text}")
    assert response.status_code == 200
    with get_test_session() as db:
        stmt = select(EmailVerificationCode).where(EmailVerificationCode.email == email_test).order_by(EmailVerificationCode.created_at.desc())
        verification = await db.execute(stmt).scalars().scalars().first()
        assert verification is not None
        verification_code = str(verification.code)
        response = client.post("/api/verify-email-code", json={"email": email_test, "code": verification_code})
        print(f"Verify email for login: {response.status_code}, response: {response.text}")
        assert response.status_code == 200

    # Debug: Check user ID in database
    with get_test_session() as db:
        user = db.query(User).filter(User.email == email_test).scalars().first()
        assert user is not None
        print(f"Database user ID: {user.id}, type: {type(user.id)}")

    # Test login
    login_data = {"login": email_test, "password": password_test}
    response = client.post("/api/token", json=login_data)
    print(f"Login status: {response.status_code}, response: {response.text}")
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    assert "access_token" in data
    assert data.get("token_type") == "bearer"
    print("Cookies received after login:", response.cookies.items())
    refresh_token_cookie = response.cookies.get("refresh_token")
    assert refresh_token_cookie is not None, "Refresh token cookie missing"
    
    # Debug: Decode refresh token to check payload
    from jose import jwt
    from app.config import REFRESH_SECRET_KEY, ALGORITHM
    try:
        payload = jwt.decode(refresh_token_cookie, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Refresh token payload: {payload}")
    except Exception as e:
        print(f"Error decoding refresh token: {e}")

    # Set cookies on the client instance
    client.cookies.set("refresh_token", refresh_token_cookie)

    # Test refresh token
    response_refresh = client.post("/api/refresh")  # No cookies parameter
    print(f"Refresh status: {response_refresh.status_code}, response: {response_refresh.text}")
    assert response_refresh.status_code == 200, f"Refresh token failed: {response_refresh.text}"
    refresh_data = response_refresh.json()
    assert "access_token" in refresh_data

def test_logout(client):
    response = client.post("/api/logout")
    print(f"Logout status: {response.status_code}, response: {response.text}")
    assert response.status_code == 200
    assert response.json()["message"] == "Déconnecté"

async def test_read_user_me(client, email_test, unique_username, password_test):
    # Register and verify user
    user_data = {
        "username": unique_username,
        "email": email_test,
        "password": password_test,
        "name": "TestUser",
    }
    response = client.post("/api/register", json=user_data)
    print(f"Register for user_me: {response.status_code}, response: {response.text}")
    assert response.status_code == 200
    response_data = response.json()
    user_id = response_data["id"]
    print(f"Registered user ID: {user_id}, type: {type(user_id)}")

    response = client.post("/api/request-email-verification", json={"email": email_test})
    print(f"Request email verification for user_me: {response.status_code}, response: {response.text}")
    assert response.status_code == 200
    with get_test_session() as db:
        stmt = select(EmailVerificationCode).where(EmailVerificationCode.email == email_test).order_by(EmailVerificationCode.created_at.desc())
        verification = await db.execute(stmt).scalars().scalars().first()
        assert verification is not None
        verification_code = str(verification.code)
        response = client.post("/api/verify-email-code", json={"email": email_test, "code": verification_code})
        print(f"Verify email for user_me: {response.status_code}, response: {response.text}")
        assert response.status_code == 200

    # Debug: Check user ID in database
    with get_test_session() as db:
        user = db.query(User).filter(User.email == email_test).scalars().first()
        assert user is not None
        print(f"Database user ID: {user.id}, type: {type(user.id)}")

    # Login to get token
    login_data = {"login": email_test, "password": password_test}
    login_resp = client.post("/api/token", json=login_data)
    print(f"Login for user_me status: {login_resp.status_code}, response: {login_resp.text}")
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    # Debug: Decode access token to check payload
    from jose import jwt
    from app.config import SECRET_KEY, ALGORITHM
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Access token payload: {payload}")
    except Exception as e:
        print(f"Error decoding access token: {e}")

    # Test user/me endpoint
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/user/me", headers=headers)
    print(f"User/me status: {response.status_code}, response: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert "email" in data

async def test_create_and_get_bots(client, email_test, unique_username, password_test):
    # Register and verify user
    user_data = {
        "username": unique_username,
        "email": email_test,
        "password": password_test,
        "name": "TestUser",
    }
    response = client.post("/api/register", json=user_data)
    print(f"Register for bots: {response.status_code}, response: {response.text}")
    assert response.status_code == 200
    response_data = response.json()
    user_id = response_data["id"]
    print(f"Registered user ID: {user_id}, type: {type(user_id)}")

    response = client.post("/api/request-email-verification", json={"email": email_test})
    print(f"Request email verification for bots: {response.status_code}, response: {response.text}")
    assert response.status_code == 200
    with get_test_session() as db:
        stmt = select(EmailVerificationCode).where(EmailVerificationCode.email == email_test).order_by(EmailVerificationCode.created_at.desc())
        verification = await db.execute(stmt).scalars().scalars().first()
        assert verification is not None
        verification_code = str(verification.code)
        response = client.post("/api/verify-email-code", json={"email": email_test, "code": verification_code})
        print(f"Verify email for bots: {response.status_code}, response: {response.text}")
        assert response.status_code == 200

    # Create a subscription for the user
    with get_test_session() as db:
        user = db.query(User).filter(User.email == email_test).scalars().first()
        assert user is not None
        print(f"Database user ID: {user.id}, type: {type(user.id)}")
        subscription = Subscription(
            user_id=user.id,
            plan=PlanEnum.FREE,
            status=SubscriptionStatus.active,
            created_at=datetime.now(timezone.utc)
        )
        db.add(subscription)
        await db.commit()
        print(f"Created subscription for user ID: {user.id}")

    # Login to get token
    login_data = {"login": email_test, "password": password_test}
    login_resp = client.post("/api/token", json=login_data)
    print(f"Login for bots status: {login_resp.status_code}, response: {login_resp.text}")
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    # Debug: Decode access token to check payload
    from jose import jwt
    from app.config import SECRET_KEY, ALGORITHM
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Access token payload: {payload}")
    except Exception as e:
        print(f"Error decoding access token: {e}")

    # Create bot
    bot_data = {"name": "TestBot"}
    response = client.post("/api/create_bot", json=bot_data, headers={"Authorization": f"Bearer {token}"})
    print(f"Create bot status: {response.status_code}, response: {response.text}")
    assert response.status_code == 200
    bot_info = response.json()
    assert "bot_id" in bot_info
    assert "conversation_id" in bot_info

    # Get bots
    response = client.get("/api/my_bots", headers={"Authorization": f"Bearer {token}"})
    print(f"My bots status: {response.status_code}, response: {response.text}")
    assert response.status_code == 200
    bots = response.json()
    assert any(bot["bot_id"] == bot_info["bot_id"] for bot in bots)

async def test_change_password(client, email_test, unique_username, password_test):
    # Register and verify user
    user_data = {
        "username": unique_username,
        "email": email_test,
        "password": password_test,
        "name": "TestUser",
    }
    response = client.post("/api/register", json=user_data)
    print(f"Register for change password: {response.status_code}, response: {response.text}")
    assert response.status_code == 200
    response_data = response.json()
    user_id = response_data["id"]
    print(f"Registered user ID: {user_id}, type: {type(user_id)}")

    response = client.post("/api/request-email-verification", json={"email": email_test})
    print(f"Request email verification for change password: {response.status_code}, response: {response.text}")
    assert response.status_code == 200
    with get_test_session() as db:
        stmt = select(EmailVerificationCode).where(EmailVerificationCode.email == email_test).order_by(EmailVerificationCode.created_at.desc())
        verification = await db.execute(stmt).scalars().scalars().first()
        assert verification is not None
        verification_code = str(verification.code)
        response = client.post("/api/verify-email-code", json={"email": email_test, "code": verification_code})
        print(f"Verify email for change password: {response.status_code}, response: {response.text}")
        assert response.status_code == 200

    # Debug: Check user ID in database
    with get_test_session() as db:
        user = db.query(User).filter(User.email == email_test).scalars().first()
        assert user is not None
        print(f"Database user ID: {user.id}, type: {type(user.id)}")

    # Login to get token
    login_data = {"login": email_test, "password": password_test}
    login_resp = client.post("/api/token", json=login_data)
    print(f"Login for change password status: {login_resp.status_code}, response: {login_resp.text}")
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    # Debug: Decode access token to check payload
    from jose import jwt
    from app.config import SECRET_KEY, ALGORITHM
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Access token payload: {payload}")
    except Exception as e:
        print(f"Error decoding access token: {e}")

    # Change password
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "old_password": password_test,
        "new_password": "newStrongPassword123"
    }
    response = client.post("/api/user/change-password", json=payload, headers=headers)
    print(f"Change password status: {response.status_code}, response: {response.text}")
    assert response.status_code == 200
    assert "Mot de passe mis à jour" in response.json()["detail"]