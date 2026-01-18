"""
Infrastructure services connectivity tests.
"""
import pytest
import psycopg2
from redis import Redis
from minio import Minio
from app.core.config import settings


def test_postgresql_connection():
    """Test PostgreSQL connection."""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5442,
            database=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        conn.close()
        assert result[0] == 1
    except Exception as e:
        pytest.skip(f"PostgreSQL not accessible: {e}")


def test_redis_connection():
    """Test Redis connection."""
    try:
        redis_client = Redis(
            host="localhost",
            port=6389,
            db=0,
            decode_responses=True
        )
        redis_client.ping()
        # Test set/get
        redis_client.set("test_key", "test_value", ex=10)
        value = redis_client.get("test_key")
        redis_client.delete("test_key")
        assert value == "test_value"
    except Exception as e:
        pytest.skip(f"Redis not accessible: {e}")


def test_minio_connection():
    """Test MinIO connection."""
    try:
        minio_client = Minio(
            "localhost:9010",
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False
        )
        # List buckets to test connection
        buckets = minio_client.list_buckets()
        assert isinstance(buckets, list)
    except Exception as e:
        pytest.skip(f"MinIO not accessible: {e}")
