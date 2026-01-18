"""
Security tests.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.core.security import get_password_hash, verify_password


@pytest.fixture
def client(db):
    """Create test client."""
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


def test_password_hashing():
    """Test that passwords are hashed, not stored in plain text."""
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert len(hashed) > len(password)
    assert hashed.startswith("$2b$")  # bcrypt hash format


def test_password_verification():
    """Test password verification."""
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_invalid_token_rejected(client):
    """Test that invalid tokens are rejected."""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token_here"}
    )
    assert response.status_code == 401


def test_sql_injection_prevention(client, db):
    """Test SQL injection prevention."""
    # Try SQL injection in email field
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin' OR '1'='1",
            "password": "anything"
        }
    )
    # Should fail authentication, not execute SQL
    assert response.status_code == 401


def test_file_upload_validation(client, db):
    """Test file upload validation."""
    user = User(
        email="upload@example.com",
        username="uploaduser",
        hashed_password=get_password_hash("password")
    )
    db.add(user)
    db.commit()
    
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "upload@example.com", "password": "password"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try uploading invalid file type
    from io import BytesIO
    invalid_file = BytesIO(b"fake_executable")
    files = {"file": ("test.exe", invalid_file, "application/x-msdownload")}
    
    response = client.post(
        "/api/v1/canvas/upload",
        files=files,
        headers=headers
    )
    # Should reject invalid file type
    assert response.status_code in [400, 415]
