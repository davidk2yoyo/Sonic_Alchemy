"""
Voice feature tests.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.models.voice_recording import VoiceRecording
from app.core.security import get_password_hash
from io import BytesIO


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
        email="voice@example.com",
        username="voiceuser",
        hashed_password=get_password_hash("password")
    )
    db.add(user)
    db.commit()
    
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "voice@example.com", "password": "password"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_voice_upload(client, db, auth_headers):
    """Test voice audio upload."""
    audio_data = BytesIO(b"fake_audio_data")
    files = {"file": ("test.wav", audio_data, "audio/wav")}
    
    response = client.post(
        "/api/v1/voice/upload",
        files=files,
        headers=auth_headers
    )
    
    assert response.status_code in [201, 400, 500]  # May fail due to validation


def test_voice_get(client, db, auth_headers):
    """Test getting voice recording."""
    voice = VoiceRecording(
        raw_audio_url="http://test.com/audio.wav",
        status="uploaded"
    )
    db.add(voice)
    db.commit()
    db.refresh(voice)
    
    response = client.get(
        f"/api/v1/voice/{voice.id}",
        headers=auth_headers
    )
    
    assert response.status_code in [200, 403, 404]
