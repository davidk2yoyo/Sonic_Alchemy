"""
Voice processing endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.voice_recording import VoiceRecording
from app.models.project import Project
from app.api.v1.auth import get_current_user
from app.services.storage_service import storage_service
from app.services.audio_service import audio_service
from app.tasks.audio_processing import process_voice_audio_task, apply_style_transfer_task
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime
import uuid

router = APIRouter()


class VoiceCorrections(BaseModel):
    """Voice correction options."""
    pitch_correction: bool = True
    timing_quantization: bool = True
    breath_control: bool = False


class VoiceResponse(BaseModel):
    """Voice recording response model."""
    id: int
    raw_audio_url: str
    processed_audio_url: Optional[str]
    style: Optional[str]
    status: str
    duration_seconds: Optional[float]
    created_at: str
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj: VoiceRecording):
        """Convert VoiceRecording model to response."""
        return cls(
            id=obj.id,
            raw_audio_url=obj.raw_audio_url,
            processed_audio_url=obj.processed_audio_url,
            style=obj.style,
            status=obj.status,
            duration_seconds=obj.duration_seconds,
            created_at=obj.created_at.isoformat() if obj.created_at else ""
        )


@router.post("/voice/upload", response_model=VoiceResponse, status_code=status.HTTP_201_CREATED)
async def upload_voice(
    file: UploadFile = File(...),
    project_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload raw audio file."""
    # Validate file type
    file_ext = file.filename.split('.')[-1].lower() if file.filename else ''
    if file_ext not in settings.allowed_audio_formats_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file format. Allowed: {settings.ALLOWED_AUDIO_FORMATS}"
        )
    
    # Read file data
    file_data = await file.read()
    
    # Validate file size
    file_size_mb = len(file_data) / (1024 * 1024)
    if file_size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum: {settings.MAX_UPLOAD_SIZE_MB}MB"
        )
    
    # Get audio duration
    try:
        duration = audio_service.get_audio_duration(file_data)
        if duration > settings.MAX_AUDIO_DURATION_SECONDS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Audio too long. Maximum: {settings.MAX_AUDIO_DURATION_SECONDS} seconds"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid audio file: {str(e)}"
        )
    
    # Generate object name
    object_name = f"{current_user.id}/{uuid.uuid4()}/{file.filename}"
    
    # Upload to MinIO
    try:
        audio_url = storage_service.upload_file(
            bucket_name=settings.MINIO_BUCKET_AUDIO,
            object_name=object_name,
            file_data=file_data,
            content_type=file.content_type or "audio/wav"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload audio: {str(e)}"
        )
    
    # Create voice recording record
    voice_recording = VoiceRecording(
        project_id=project_id,
        raw_audio_url=audio_url,
        duration_seconds=duration,
        status="uploaded"
    )
    
    db.add(voice_recording)
    db.commit()
    db.refresh(voice_recording)
    
    # Convert to response model
    return VoiceResponse.from_orm(voice_recording)


@router.post("/voice/process")
async def process_voice(
    voice_id: int,
    corrections: VoiceCorrections,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process voice with corrections."""
    # Get voice recording
    voice = db.query(VoiceRecording).filter(VoiceRecording.id == voice_id).first()
    
    if not voice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voice recording not found"
        )
    
    # Check access
    if voice.project_id:
        project = db.query(Project).filter(Project.id == voice.project_id).first()
        if project and project.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    # Update status
    voice.status = "processing"
    db.commit()
    
    # Queue async task
    try:
        task = process_voice_audio_task.delay(
            voice_id,
            corrections.dict()
        )
        return {
            "task_id": task.id,
            "status": "processing",
            "voice_id": voice_id,
            "message": "Voice processing started"
        }
    except Exception as e:
        voice.status = "failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start processing: {str(e)}"
        )


@router.post("/voice/style-transfer")
async def style_transfer(
    voice_id: int,
    style: str,
    reference_audio: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Apply style transfer to voice."""
    # Get voice recording
    voice = db.query(VoiceRecording).filter(VoiceRecording.id == voice_id).first()
    
    if not voice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voice recording not found"
        )
    
    # Check access
    if voice.project_id:
        project = db.query(Project).filter(Project.id == voice.project_id).first()
        if project and project.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    # Handle reference audio if provided
    reference_audio_url = None
    if reference_audio:
        ref_data = await reference_audio.read()
        ref_object_name = f"{current_user.id}/{uuid.uuid4()}/{reference_audio.filename}"
        reference_audio_url = storage_service.upload_file(
            bucket_name=settings.MINIO_BUCKET_AUDIO,
            object_name=ref_object_name,
            file_data=ref_data,
            content_type=reference_audio.content_type or "audio/wav"
        )
    
    # Update status
    voice.status = "processing"
    voice.style = style
    db.commit()
    
    # Queue async task
    try:
        task = apply_style_transfer_task.delay(
            voice_id,
            style,
            reference_audio_url
        )
        return {
            "task_id": task.id,
            "status": "processing",
            "voice_id": voice_id,
            "style": style,
            "message": "Style transfer started"
        }
    except Exception as e:
        voice.status = "failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start style transfer: {str(e)}"
        )


@router.get("/voice/{voice_id}", response_model=VoiceResponse)
async def get_voice(
    voice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get voice recording details."""
    voice = db.query(VoiceRecording).filter(VoiceRecording.id == voice_id).first()
    
    if not voice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voice recording not found"
        )
    
    # Check access
    if voice.project_id:
        project = db.query(Project).filter(Project.id == voice.project_id).first()
        if project and project.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return VoiceResponse.from_orm(voice)
