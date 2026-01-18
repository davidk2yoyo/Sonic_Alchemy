"""
Authentication tests.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.core.security import get_password_hash


@pytest.fixture
def client(db):
    """Create test client."""
    from app.main import app
    from app.core.database import get_db
    
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_user_registration(client, db):
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "testpassword123"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "user" in data
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "newuser@example.com"
    assert data["user"]["username"] == "newuser"


def test_user_registration_duplicate_email(client, db):
    """Test registration with duplicate email."""
    # Create user first
    user = User(
        email="duplicate@example.com",
        username="firstuser",
        hashed_password=get_password_hash("password")
    )
    db.add(user)
    db.commit()
    
    # Try to register with same email
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "username": "seconduser",
            "password": "password123"
        }
    )
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_user_login(client, db):
    """Test user login."""
    # Create user first
    user = User(
        email="login@example.com",
        username="loginuser",
        hashed_password=get_password_hash("testpassword")
    )
    db.add(user)
    db.commit()
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@example.com",
            "password": "testpassword"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_user_login_invalid_credentials(client, db):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


def test_token_validation(client, db):
    """Test token validation."""
    # Create user and get token
    user = User(
        email="token@example.com",
        username="tokenuser",
        hashed_password=get_password_hash("password")
    )
    db.add(user)
    db.commit()
    
    # Login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "token@example.com",
            "password": "password"
        }
    )
    token = login_response.json()["access_token"]
    
    # Use token to access protected endpoint
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "token@example.com"


def test_invalid_token(client):
    """Test access with invalid token."""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token_here"}
    )
    
    assert response.status_code == 401


def test_token_refresh(client, db):
    """Test token refresh."""
    # Create user and get refresh token
    user = User(
        email="refresh@example.com",
        username="refreshuser",
        hashed_password=get_password_hash("password")
    )
    db.add(user)
    db.commit()
    
    # Login to get tokens
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "refresh@example.com",
            "password": "password"
        }
    )
    refresh_token = login_response.json()["refresh_token"]
    
    # Refresh access token
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
