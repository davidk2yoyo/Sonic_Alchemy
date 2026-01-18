"""
Storage service for MinIO/S3 file operations.
"""
from minio import Minio
from minio.error import S3Error
from app.core.config import settings
import logging
from typing import Optional
from io import BytesIO

logger = logging.getLogger(__name__)


class StorageService:
    """Service for file storage operations."""
    
    def __init__(self):
        """Initialize MinIO client."""
        try:
            # Get endpoint, default to localhost if running outside Docker
            endpoint = settings.MINIO_ENDPOINT
            if endpoint == "minio:9000" or "minio:" in endpoint:
                # Running locally, use localhost
                endpoint = "localhost:9010"
            
            self.client = Minio(
                endpoint,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_USE_SSL
            )
            self._ensure_buckets()
            logger.info(f"MinIO client initialized with endpoint: {endpoint}")
        except Exception as e:
            logger.error(f"Failed to initialize MinIO client: {e}")
            self.client = None
    
    def _ensure_buckets(self):
        """Ensure required buckets exist."""
        if not self.client:
            return
        
        buckets = [settings.MINIO_BUCKET_AUDIO, settings.MINIO_BUCKET_IMAGES]
        
        for bucket_name in buckets:
            try:
                if not self.client.bucket_exists(bucket_name):
                    self.client.make_bucket(bucket_name)
                    logger.info(f"Created bucket: {bucket_name}")
            except S3Error as e:
                logger.error(f"Error creating bucket {bucket_name}: {e}")
    
    def upload_file(
        self,
        bucket_name: str,
        object_name: str,
        file_data: bytes,
        content_type: str = "application/octet-stream"
    ) -> str:
        """
        Upload file to MinIO.
        
        Args:
            bucket_name: Bucket name
            object_name: Object name (path)
            file_data: File bytes
            content_type: MIME type
            
        Returns:
            Object URL
        """
        if not self.client:
            raise Exception("MinIO client not initialized")
        
        try:
            file_obj = BytesIO(file_data)
            file_size = len(file_data)
            
            logger.info(f"Uploading to bucket '{bucket_name}', object '{object_name}', size: {file_size} bytes")
            
            self.client.put_object(
                bucket_name,
                object_name,
                file_obj,
                file_size,
                content_type=content_type
            )
            
            logger.info(f"File uploaded successfully to MinIO")
            
            # Return object URL (use presigned URL for better access)
            try:
                from datetime import timedelta
                url = self.client.presigned_get_object(
                    bucket_name,
                    object_name,
                    expires=timedelta(hours=24)
                )
                logger.info(f"Generated presigned URL for {object_name}")
                return url
            except Exception as e:
                logger.warning(f"Failed to generate presigned URL: {e}, using direct URL")
                # Fallback to direct URL
                endpoint = settings.MINIO_ENDPOINT
                if endpoint == "minio:9000" or "minio:" in endpoint:
                    endpoint = "localhost:9010"
                # Use http:// for local development
                protocol = "https://" if settings.MINIO_USE_SSL else "http://"
                url = f"{protocol}{endpoint}/{bucket_name}/{object_name}"
                logger.info(f"Using direct URL: {url}")
                return url
            
        except S3Error as e:
            logger.error(f"Error uploading file: {e}")
            raise Exception(f"Failed to upload file: {str(e)}")
    
    def get_file(self, bucket_name: str, object_name: str) -> bytes:
        """
        Get file from MinIO.
        
        Args:
            bucket_name: Bucket name
            object_name: Object name (path)
            
        Returns:
            File bytes
        """
        if not self.client:
            raise Exception("MinIO client not initialized")
        
        try:
            response = self.client.get_object(bucket_name, object_name)
            file_data = response.read()
            response.close()
            response.release_conn()
            
            return file_data
            
        except S3Error as e:
            logger.error(f"Error getting file: {e}")
            raise Exception(f"Failed to get file: {str(e)}")
    
    def delete_file(self, bucket_name: str, object_name: str):
        """
        Delete file from MinIO.
        
        Args:
            bucket_name: Bucket name
            object_name: Object name (path)
        """
        if not self.client:
            raise Exception("MinIO client not initialized")
        
        try:
            self.client.remove_object(bucket_name, object_name)
            
        except S3Error as e:
            logger.error(f"Error deleting file: {e}")
            raise Exception(f"Failed to delete file: {str(e)}")
    
    def generate_presigned_url(
        self,
        bucket_name: str,
        object_name: str,
        expires_seconds: int = 3600
    ) -> str:
        """
        Generate presigned URL for temporary access.
        
        Args:
            bucket_name: Bucket name
            object_name: Object name (path)
            expires_seconds: URL expiration time
            
        Returns:
            Presigned URL
        """
        if not self.client:
            raise Exception("MinIO client not initialized")
        
        try:
            from datetime import timedelta
            url = self.client.presigned_get_object(
                bucket_name,
                object_name,
                expires=timedelta(seconds=expires_seconds)
            )
            return url
            
        except S3Error as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise Exception(f"Failed to generate presigned URL: {str(e)}")


# Create singleton instance
storage_service = StorageService()
