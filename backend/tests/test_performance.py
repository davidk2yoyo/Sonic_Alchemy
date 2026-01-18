"""
Performance tests.
"""
import pytest
import time
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


def test_api_response_time(client, db):
    """Test that API endpoints respond within acceptable time."""
    # Health check should be fast
    start = time.time()
    response = client.get("/health")
    elapsed = time.time() - start
    
    assert response.status_code == 200
    assert elapsed < 1.0  # Should respond in less than 1 second


def test_concurrent_requests(client, db):
    """Test handling of concurrent requests."""
    import concurrent.futures
    
    def make_request():
        return client.get("/health")
    
    # Make 10 concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(10)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    # All should succeed
    assert all(r.status_code == 200 for r in results)
    assert len(results) == 10
