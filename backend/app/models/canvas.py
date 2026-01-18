"""
Canvas model for image analysis and music generation.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Canvas(Base):
    """Canvas model for image emotion analysis and music generation."""
    
    __tablename__ = "canvases"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True)
    image_url = Column(String(500), nullable=False)
    emotion_analysis = Column(JSON, default=dict)
    music_generation_prompt = Column(Text)
    generated_music_url = Column(String(500))
    status = Column(String(50), default="pending", nullable=False)  # pending, analyzed, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", foreign_keys=[project_id])
