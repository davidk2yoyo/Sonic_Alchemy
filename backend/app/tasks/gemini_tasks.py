"""
Celery tasks for Gemini API operations.
"""
from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.canvas import Canvas
from app.services.storage_service import storage_service
from app.services.canvas_service import canvas_service
from app.services.gemini_service import gemini_service
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="analyze_image_emotion")
def analyze_image_emotion_task(canvas_id: int):
    """
    Analyze image emotion using Gemini Vision API.
    
    Args:
        canvas_id: Canvas ID to analyze
        
    Returns:
        Analysis results
    """
    db = SessionLocal()
    try:
        # Get canvas
        canvas = db.query(Canvas).filter(Canvas.id == canvas_id).first()
        
        if not canvas:
            logger.error(f"Canvas {canvas_id} not found")
            return {"error": "Canvas not found"}
        
        # Get image from storage
        try:
            # Extract object name from URL
            object_name = canvas.image_url.split(f"{settings.MINIO_BUCKET_IMAGES}/")[-1]
            image_data = storage_service.get_file(
                bucket_name=settings.MINIO_BUCKET_IMAGES,
                object_name=object_name
            )
        except Exception as e:
            logger.error(f"Failed to get image: {e}")
            canvas.status = "failed"
            db.commit()
            return {"error": str(e)}
        
        # Analyze emotion
        try:
            emotion_analysis = canvas_service.analyze_emotion(image_data)
            
            # Update canvas
            canvas.emotion_analysis = emotion_analysis
            canvas.status = "analyzed"
            db.commit()
            
            logger.info(f"Canvas {canvas_id} analyzed successfully")
            return {
                "canvas_id": canvas_id,
                "status": "analyzed",
                "emotion_analysis": emotion_analysis
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze emotion: {e}")
            canvas.status = "failed"
            db.commit()
            return {"error": str(e)}
            
    finally:
        db.close()


@celery_app.task(name="generate_music")
def generate_music_task(canvas_id: int, duration_seconds: int = 60, style: str = None):
    """
    Generate music from canvas analysis.
    
    Args:
        canvas_id: Canvas ID
        duration_seconds: Music duration
        style: Optional music style
        
    Returns:
        Generated music URL
    """
    db = SessionLocal()
    try:
        # Get canvas
        canvas = db.query(Canvas).filter(Canvas.id == canvas_id).first()
        
        if not canvas:
            logger.error(f"Canvas {canvas_id} not found")
            return {"error": "Canvas not found"}
        
        if not canvas.emotion_analysis:
            logger.error(f"Canvas {canvas_id} not analyzed")
            canvas.status = "failed"
            db.commit()
            return {"error": "Canvas must be analyzed first"}
        
        # Generate music prompt
        music_prompt = canvas_service.generate_music_prompt(canvas.emotion_analysis)
        
        # For MVP, we'll store the prompt
        # Actual music generation would require external service or model
        # TODO: Integrate with music generation service
        
        # For now, mark as completed with placeholder
        canvas.music_generation_prompt = music_prompt
        canvas.status = "completed"
        # canvas.generated_music_url = "placeholder"  # Will be set when music is generated
        db.commit()
        
        logger.info(f"Music generation prompt created for canvas {canvas_id}")
        return {
            "canvas_id": canvas_id,
            "status": "completed",
            "prompt": music_prompt,
            "message": "Music generation prompt created (actual generation pending)"
        }
        
    except Exception as e:
        logger.error(f"Failed to generate music: {e}")
        if canvas:
            canvas.status = "failed"
            db.commit()
        return {"error": str(e)}
        
    finally:
        db.close()
