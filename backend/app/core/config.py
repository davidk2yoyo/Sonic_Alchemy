"""
Application configuration using Pydantic Settings.
Loads and validates all environment variables.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    POSTGRES_DB: str = Field(default="voicecanvas")
    POSTGRES_USER: str = Field(default="voicecanvas")
    POSTGRES_PASSWORD: str = Field(default="voicecanvas_dev_password")
    POSTGRES_HOST: str = Field(default="postgres")
    POSTGRES_PORT: int = Field(default=5432)
    DATABASE_URL: str = Field(default="")
    
    # Redis Configuration
    REDIS_URL: str = Field(default="redis://redis:6379/0")
    REDIS_HOST: str = Field(default="redis")
    REDIS_PORT: int = Field(default=6379)
    REDIS_DB: int = Field(default=0)
    CACHE_TTL: int = Field(default=3600)
    
    # MinIO/S3 Storage
    MINIO_ENDPOINT: str = Field(default="minio:9000")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin")
    MINIO_SECRET_KEY: str = Field(default="minioadmin")
    MINIO_BUCKET_AUDIO: str = Field(default="audio")
    MINIO_BUCKET_IMAGES: str = Field(default="images")
    MINIO_USE_SSL: bool = Field(default=False)
    
    # Gemini API
    GEMINI_API_KEY: str = Field(default="")
    GEMINI_MODEL_VISION: str = Field(default="gemini-pro-vision")
    GEMINI_MODEL_AUDIO: str = Field(default="gemini-pro")
    GEMINI_MODEL_TEXT: str = Field(default="gemini-pro")
    GEMINI_RATE_LIMIT: int = Field(default=60)
    GEMINI_CACHE_ENABLED: bool = Field(default=True)
    
    # Security
    SECRET_KEY: str = Field(default="dev_secret_key_change_in_production")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
    PASSWORD_HASH_ALGORITHM: str = Field(default="bcrypt")
    
    # Application Settings
    ENVIRONMENT: str = Field(default="development")
    API_V1_PREFIX: str = Field(default="/api/v1")
    CORS_ORIGINS: str = Field(default="http://localhost:3010")
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000)
    LOG_LEVEL: str = Field(default="INFO")
    
    # Celery Configuration
    CELERY_BROKER_URL: str = Field(default="redis://redis:6379/0")
    CELERY_RESULT_BACKEND: str = Field(default="redis://redis:6379/0")
    CELERY_TASK_SERIALIZER: str = Field(default="json")
    CELERY_RESULT_SERIALIZER: str = Field(default="json")
    CELERY_ACCEPT_CONTENT: List[str] = Field(default=["json"])
    
    # File Upload Limits
    MAX_UPLOAD_SIZE_MB: int = Field(default=50)
    MAX_AUDIO_DURATION_SECONDS: int = Field(default=300)
    ALLOWED_IMAGE_FORMATS: str = Field(default="jpg,jpeg,png,webp")
    ALLOWED_AUDIO_FORMATS: str = Field(default="wav,mp3,m4a,ogg")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Build DATABASE_URL if not provided
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def allowed_image_formats_list(self) -> List[str]:
        """Parse ALLOWED_IMAGE_FORMATS string into list."""
        return [fmt.strip().lower() for fmt in self.ALLOWED_IMAGE_FORMATS.split(",")]
    
    @property
    def allowed_audio_formats_list(self) -> List[str]:
        """Parse ALLOWED_AUDIO_FORMATS string into list."""
        return [fmt.strip().lower() for fmt in self.ALLOWED_AUDIO_FORMATS.split(",")]


# Create settings instance
settings = Settings()
