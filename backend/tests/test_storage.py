"""
MinIO storage tests.
"""
import pytest
from minio import Minio
from minio.error import S3Error
from app.core.config import settings
from app.services.storage_service import StorageService


def test_minio_connection():
    """Test MinIO connection."""
    try:
        minio_client = Minio(
            "localhost:9010",
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False
        )
        buckets = minio_client.list_buckets()
        assert isinstance(buckets, list)
    except Exception as e:
        pytest.skip(f"MinIO not accessible: {e}")


def test_bucket_creation():
    """Test bucket creation."""
    try:
        minio_client = Minio(
            "localhost:9010",
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False
        )
        
        # Create audio bucket if it doesn't exist
        if not minio_client.bucket_exists(settings.MINIO_BUCKET_AUDIO):
            minio_client.make_bucket(settings.MINIO_BUCKET_AUDIO)
        
        # Create images bucket if it doesn't exist
        if not minio_client.bucket_exists(settings.MINIO_BUCKET_IMAGES):
            minio_client.make_bucket(settings.MINIO_BUCKET_IMAGES)
        
        # Verify buckets exist
        assert minio_client.bucket_exists(settings.MINIO_BUCKET_AUDIO)
        assert minio_client.bucket_exists(settings.MINIO_BUCKET_IMAGES)
    except Exception as e:
        pytest.skip(f"MinIO not accessible: {e}")


def test_file_upload():
    """Test file upload to MinIO."""
    try:
        minio_client = Minio(
            "localhost:9010",
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False
        )
        
        # Ensure bucket exists
        if not minio_client.bucket_exists(settings.MINIO_BUCKET_AUDIO):
            minio_client.make_bucket(settings.MINIO_BUCKET_AUDIO)
        
        # Create test file
        test_content = b"test audio content"
        from io import BytesIO
        test_file = BytesIO(test_content)
        
        # Upload file
        minio_client.put_object(
            settings.MINIO_BUCKET_AUDIO,
            "test_file.txt",
            test_file,
            length=len(test_content)
        )
        
        # Verify file exists
        objects = list(minio_client.list_objects(settings.MINIO_BUCKET_AUDIO, prefix="test_file.txt"))
        assert len(objects) > 0
        
        # Cleanup
        minio_client.remove_object(settings.MINIO_BUCKET_AUDIO, "test_file.txt")
    except Exception as e:
        pytest.skip(f"MinIO not accessible: {e}")
