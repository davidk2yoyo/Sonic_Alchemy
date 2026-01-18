"""
End-to-end integration tests.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.core.security import get_password_hash


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


def test_user_registration_and_login_flow(client, db):
    """Test complete user registration and login flow."""
    # Register
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "e2e@example.com",
            "username": "e2euser",
            "password": "password123"
        }
    )
    assert register_response.status_code == 201
    assert "access_token" in register_response.json()
    
    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "e2e@example.com",
            "password": "password123"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # Access protected endpoint
    headers = {"Authorization": f"Bearer {token}"}
    me_response = client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "e2e@example.com"


def test_project_creation_flow(client, db):
    """Test project creation flow."""
    # Create user and login
    user = User(
        email="projectflow@example.com",
        username="projectflow",
        hashed_password=get_password_hash("password")
    )
    db.add(user)
    db.commit()
    
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "projectflow@example.com", "password": "password"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create project
    project_response = client.post(
        "/api/v1/projects",
        json={"title": "E2E Test Project", "description": "Test"},
        headers=headers
    )
    assert project_response.status_code == 201
    project_id = project_response.json()["id"]
    
    # Get project
    get_response = client.get(f"/api/v1/projects/{project_id}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "E2E Test Project"
