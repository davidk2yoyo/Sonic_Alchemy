"""
Voice recording model for audio processing.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class VoiceRecording(Base):
    """Voice recording model for audio files and processing metadata."""
    
    __tablename__ = "voice_recordings"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True)
    raw_audio_url = Column(String(500), nullable=False)
    processed_audio_url = Column(String(500))
    style = Column(String(100))
    corrections_applied = Column(JSON, default=dict)
    status = Column(String(50), default="pending", nullable=False)  # pending, processing, completed, failed
    duration_seconds = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="voice_recording")
