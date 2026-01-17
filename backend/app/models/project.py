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
    metadata = Column(JSON, default=dict)
    is_public = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    canvas = relationship("Canvas", back_populates="project", uselist=False)
    voice_recording = relationship("VoiceRecording", back_populates="project", uselist=False)
    lyrics = relationship("Lyrics", back_populates="project", uselist=False)
