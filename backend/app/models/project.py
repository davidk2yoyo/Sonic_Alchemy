"""
Project model for user music projects.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Project(Base):
    """Project model representing user music projects."""
    
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    canvas_id = Column(Integer, ForeignKey("canvases.id", ondelete="SET NULL"), nullable=True)
    voice_recording_id = Column(Integer, ForeignKey("voice_recordings.id", ondelete="SET NULL"), nullable=True)
    lyrics_id = Column(Integer, ForeignKey("lyrics.id", ondelete="SET NULL"), nullable=True)
    project_metadata = Column(JSON, default=dict)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    is_public = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    # Note: Canvas, VoiceRecording, and Lyrics have project_id FK to projects.id
    # We use viewonly=True to avoid circular relationship issues
    canvas = relationship("Canvas", foreign_keys=[canvas_id], uselist=False, viewonly=True)
    voice_recording = relationship("VoiceRecording", foreign_keys=[voice_recording_id], uselist=False, viewonly=True)
    lyrics = relationship("Lyrics", foreign_keys=[lyrics_id], uselist=False, viewonly=True)
