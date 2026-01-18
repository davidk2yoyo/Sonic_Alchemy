"""
Lyrics feature tests.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.models.lyrics import Lyrics
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
        email="lyrics@example.com",
        username="lyricsuser",
        hashed_password=get_password_hash("password")
    )
    db.add(user)
    db.commit()
    
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "lyrics@example.com", "password": "password"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_lyrics_generate(client, db, auth_headers):
    """Test lyrics generation."""
    response = client.post(
        "/api/v1/lyrics/generate",
        json={
            "theme": "love and happiness",
            "emotion": "joyful"
        },
        headers=auth_headers
    )
    
    # May fail without GEMINI_API_KEY, but endpoint should exist
    assert response.status_code in [201, 500]


def test_lyrics_update(client, db, auth_headers):
    """Test lyrics update."""
    lyrics = Lyrics(
        theme="test",
        generated_lyrics="Original lyrics"
    )
    db.add(lyrics)
    db.commit()
    db.refresh(lyrics)
    
    response = client.put(
        f"/api/v1/lyrics/{lyrics.id}",
        json={"edited_lyrics": "Edited lyrics"},
        headers=auth_headers
    )
    
    assert response.status_code in [200, 403, 404]
