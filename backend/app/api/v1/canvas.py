"""
Canvas endpoints for image upload and emotion analysis.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.canvas import Canvas
from app.models.project import Project
from app.api.v1.auth import get_current_user
from app.services.storage_service import storage_service
from app.services.canvas_service import canvas_service
from app.tasks.gemini_tasks import analyze_image_emotion_task, generate_music_task
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

router = APIRouter()


class CanvasResponse(BaseModel):
    """Canvas response model."""
    id: int
    image_url: str
    emotion_analysis: dict
    generated_music_url: Optional[str]
    status: str
    created_at: str
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj: Canvas):
        """Convert Canvas model to response."""
        return cls(
            id=obj.id,
            image_url=obj.image_url,
            emotion_analysis=obj.emotion_analysis or {},
            generated_music_url=obj.generated_music_url,
            status=obj.status,
            created_at=obj.created_at.isoformat() if obj.created_at else ""
        )


@router.post("/canvas/upload", response_model=CanvasResponse, status_code=status.HTTP_201_CREATED)
async def upload_canvas(
    file: UploadFile = File(...),
    project_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload image for canvas analysis."""
    # Validate file type
    file_ext = file.filename.split('.')[-1].lower() if file.filename else ''
    if file_ext not in settings.allowed_image_formats_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file format. Allowed: {settings.ALLOWED_IMAGE_FORMATS}"
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
    
    # Generate object name
    object_name = f"{current_user.id}/{uuid.uuid4()}/{file.filename}"
    
    # Upload to MinIO
    import logging
    logger = logging.getLogger(__name__)
    try:
        logger.info(f"Uploading image to MinIO: {object_name}, size: {len(file_data)} bytes")
        
        if not storage_service.client:
            logger.error("MinIO client is not initialized")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Storage service is not available"
            )
        
        image_url = storage_service.upload_file(
            bucket_name=settings.MINIO_BUCKET_IMAGES,
            object_name=object_name,
            file_data=file_data,
            content_type=file.content_type or "image/jpeg"
        )
        logger.info(f"Image uploaded successfully, URL: {image_url[:100]}...")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload image to MinIO: {str(e)}", exc_info=True)
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Full traceback: {error_trace}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}"
        )
    
    # Create canvas record
    canvas = Canvas(
        project_id=project_id,
        image_url=image_url,
        status="uploaded"
    )
    
    db.add(canvas)
    db.commit()
    db.refresh(canvas)
    
    return CanvasResponse.from_orm(canvas)


@router.post("/canvas/analyze", response_model=CanvasResponse)
async def analyze_canvas(
    canvas_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze canvas image emotion using Gemini Vision."""
    # Get canvas
    canvas = db.query(Canvas).filter(Canvas.id == canvas_id).first()
    
    if not canvas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Canvas not found"
        )
    
    # Check if already analyzed
    if canvas.status == "analyzed" and canvas.emotion_analysis:
        return CanvasResponse.from_orm(canvas)
    
    # Update status
    canvas.status = "analyzing"
    db.commit()
    
    # Queue async task for analysis
    try:
        task = analyze_image_emotion_task.delay(canvas_id)
        return {
            "id": canvas.id,
            "image_url": canvas.image_url,
            "status": "analyzing",
            "task_id": task.id,
            "message": "Analysis started"
        }
    except Exception as e:
        canvas.status = "failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start analysis: {str(e)}"
        )


@router.post("/canvas/generate-music")
async def generate_music(
    canvas_id: int,
    duration_seconds: int = 60,
    style: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate music from canvas analysis."""
    # Get canvas
    canvas = db.query(Canvas).filter(Canvas.id == canvas_id).first()
    
    if not canvas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Canvas not found"
        )
    
    if canvas.status != "analyzed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Canvas must be analyzed before generating music"
        )
    
    # Update status
    canvas.status = "generating"
    db.commit()
    
    # Queue async task for music generation
    try:
        task = generate_music_task.delay(canvas_id, duration_seconds, style)
        return {
            "task_id": task.id,
            "status": "processing",
            "canvas_id": canvas_id,
            "message": "Music generation started"
        }
    except Exception as e:
        canvas.status = "failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start music generation: {str(e)}"
        )


@router.get("/canvas/{canvas_id}", response_model=CanvasResponse)
async def get_canvas(
    canvas_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get canvas details."""
    canvas = db.query(Canvas).filter(Canvas.id == canvas_id).first()
    
    if not canvas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Canvas not found"
        )
    
    # Check access (if canvas has project, verify user owns project)
    if canvas.project_id:
        project = db.query(Project).filter(Project.id == canvas.project_id).first()
        if project and project.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return CanvasResponse.from_orm(canvas)
