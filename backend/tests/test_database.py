"""
Database connection and model tests.
"""
import pytest
from app.models.user import User
from app.models.project import Project
from app.core.security import get_password_hash


def test_database_connection(db):
    """Test that database connection works."""
    assert db is not None
    # Simple query to test connection
    result = db.execute("SELECT 1").scalar()
    assert result == 1


def test_user_creation(db):
    """Test creating a user record."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpassword")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.is_active is True


def test_user_query(db):
    """Test querying user records."""
    # Create user
    user = User(
        email="query@example.com",
        username="queryuser",
        hashed_password=get_password_hash("password")
    )
    db.add(user)
    db.commit()
    
    # Query user
    found_user = db.query(User).filter(User.email == "query@example.com").first()
    assert found_user is not None
    assert found_user.username == "queryuser"


def test_project_creation(db):
    """Test creating a project with user relationship."""
    # Create user first
    user = User(
        email="project@example.com",
        username="projectuser",
        hashed_password=get_password_hash("password")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create project
    project = Project(
        user_id=user.id,
        title="Test Project",
        description="Test Description"
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    assert project.id is not None
    assert project.user_id == user.id
    assert project.title == "Test Project"
    assert project.owner.id == user.id


def test_foreign_key_constraints(db):
    """Test that foreign key constraints work."""
    # Create user
    user = User(
        email="fk@example.com",
        username="fkuser",
        hashed_password=get_password_hash("password")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create project with valid user_id
    project = Project(
        user_id=user.id,
        title="FK Test"
    )
    db.add(project)
    db.commit()
    
    # Try to create project with invalid user_id (should fail)
    invalid_project = Project(
        user_id=99999,  # Non-existent user
        title="Invalid"
    )
    db.add(invalid_project)
    
    with pytest.raises(Exception):  # Should raise integrity error
        db.commit()
    
    db.rollback()
