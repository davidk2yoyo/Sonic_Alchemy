"""
Celery tasks for audio processing operations.
"""
from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.voice_recording import VoiceRecording
from app.services.storage_service import storage_service
from app.services.voice_service import voice_service
from app.services.audio_service import audio_service
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="process_voice_audio")
def process_voice_audio_task(voice_id: int, corrections: dict):
    """
    Process voice audio with corrections.
    
    Args:
        voice_id: Voice recording ID
        corrections: Dictionary with correction flags
        
    Returns:
        Processing results
    """
    db = SessionLocal()
    try:
        # Get voice recording
        voice = db.query(VoiceRecording).filter(VoiceRecording.id == voice_id).first()
        
        if not voice:
            logger.error(f"Voice recording {voice_id} not found")
            return {"error": "Voice recording not found"}
        
        # Get raw audio from storage
        try:
            object_name = voice.raw_audio_url.split(f"{settings.MINIO_BUCKET_AUDIO}/")[-1]
            audio_data = storage_service.get_file(
                bucket_name=settings.MINIO_BUCKET_AUDIO,
                object_name=object_name
            )
        except Exception as e:
            logger.error(f"Failed to get audio: {e}")
            voice.status = "failed"
            db.commit()
            return {"error": str(e)}
        
        # Process audio
        try:
            processed_audio = voice_service.process_voice(
                audio_data=audio_data,
                corrections=corrections,
                format="wav"
            )
            
            # Upload processed audio
            processed_object_name = f"{object_name.rsplit('/', 1)[0]}/processed_{object_name.split('/')[-1]}"
            processed_url = storage_service.upload_file(
                bucket_name=settings.MINIO_BUCKET_AUDIO,
                object_name=processed_object_name,
                file_data=processed_audio,
                content_type="audio/wav"
            )
            
            # Update voice recording
            voice.processed_audio_url = processed_url
            voice.corrections_applied = corrections
            voice.status = "completed"
            db.commit()
            
            logger.info(f"Voice {voice_id} processed successfully")
            return {
                "voice_id": voice_id,
                "status": "completed",
                "processed_audio_url": processed_url
            }
            
        except Exception as e:
            logger.error(f"Failed to process audio: {e}")
            voice.status = "failed"
            db.commit()
            return {"error": str(e)}
            
    finally:
        db.close()


@celery_app.task(name="apply_style_transfer")
def apply_style_transfer_task(voice_id: int, style: str, reference_audio_url: str = None):
    """
    Apply style transfer to voice.
    
    Args:
        voice_id: Voice recording ID
        style: Style name
        reference_audio_url: Optional reference audio URL
        
    Returns:
        Style transfer results
    """
    db = SessionLocal()
    try:
        # Get voice recording
        voice = db.query(VoiceRecording).filter(VoiceRecording.id == voice_id).first()
        
        if not voice:
            logger.error(f"Voice recording {voice_id} not found")
            return {"error": "Voice recording not found"}
        
        # Get raw audio
        try:
            object_name = voice.raw_audio_url.split(f"{settings.MINIO_BUCKET_AUDIO}/")[-1]
            audio_data = storage_service.get_file(
                bucket_name=settings.MINIO_BUCKET_AUDIO,
                object_name=object_name
            )
        except Exception as e:
            logger.error(f"Failed to get audio: {e}")
            voice.status = "failed"
            db.commit()
            return {"error": str(e)}
        
        # Get reference audio if provided
        reference_audio = None
        if reference_audio_url:
            try:
                ref_object_name = reference_audio_url.split(f"{settings.MINIO_BUCKET_AUDIO}/")[-1]
                reference_audio = storage_service.get_file(
                    bucket_name=settings.MINIO_BUCKET_AUDIO,
                    object_name=ref_object_name
                )
            except Exception as e:
                logger.warning(f"Failed to get reference audio: {e}")
        
        # Apply style transfer
        try:
            styled_audio = voice_service.apply_style_transfer(
                audio_data=audio_data,
                style=style,
                reference_audio=reference_audio
            )
            
            # Upload styled audio
            styled_object_name = f"{object_name.rsplit('/', 1)[0]}/styled_{style}_{object_name.split('/')[-1]}"
            styled_url = storage_service.upload_file(
                bucket_name=settings.MINIO_BUCKET_AUDIO,
                object_name=styled_object_name,
                file_data=styled_audio,
                content_type="audio/wav"
            )
            
            # Update voice recording
            voice.processed_audio_url = styled_url
            voice.style = style
            voice.status = "completed"
            db.commit()
            
            logger.info(f"Style transfer applied to voice {voice_id}")
            return {
                "voice_id": voice_id,
                "status": "completed",
                "style": style,
                "processed_audio_url": styled_url
            }
            
        except Exception as e:
            logger.error(f"Failed to apply style transfer: {e}")
            voice.status = "failed"
            db.commit()
            return {"error": str(e)}
            
    finally:
        db.close()
