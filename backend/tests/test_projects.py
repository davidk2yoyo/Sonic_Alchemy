"""
Projects feature tests.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.models.project import Project
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


@pytest.fixture
def auth_headers(client, db):
    """Get authentication headers."""
    user = User(
        email="project@example.com",
        username="projectuser",
        hashed_password=get_password_hash("password")
    )
    db.add(user)
    db.commit()
    
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "project@example.com", "password": "password"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_project(client, db, auth_headers):
    """Test project creation."""
    response = client.post(
        "/api/v1/projects",
        json={
            "title": "Test Project",
            "description": "Test Description"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Project"


def test_list_projects(client, db, auth_headers):
    """Test listing projects."""
    # Create project first
    user = db.query(User).filter(User.email == "project@example.com").first()
    project = Project(
        user_id=user.id,
        title="List Test Project"
    )
    db.add(project)
    db.commit()
    
    response = client.get(
        "/api/v1/projects",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_project(client, db, auth_headers):
    """Test getting project."""
    user = db.query(User).filter(User.email == "project@example.com").first()
    project = Project(
        user_id=user.id,
        title="Get Test Project"
    )
    db.add(project)
    db.commit()
    
    response = client.get(
        f"/api/v1/projects/{project.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Get Test Project"


def test_update_project(client, db, auth_headers):
    """Test updating project."""
    user = db.query(User).filter(User.email == "project@example.com").first()
    project = Project(
        user_id=user.id,
        title="Original Title"
    )
    db.add(project)
    db.commit()
    
    response = client.put(
        f"/api/v1/projects/{project.id}",
        json={"title": "Updated Title"},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"


def test_delete_project(client, db, auth_headers):
    """Test deleting project."""
    user = db.query(User).filter(User.email == "project@example.com").first()
    project = Project(
        user_id=user.id,
        title="Delete Test Project"
    )
    db.add(project)
    db.commit()
    project_id = project.id
    
    response = client.delete(
        f"/api/v1/projects/{project_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 204
    
    # Verify deleted
    deleted_project = db.query(Project).filter(Project.id == project_id).first()
    assert deleted_project is None
