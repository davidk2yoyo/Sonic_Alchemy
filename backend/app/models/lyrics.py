"""
Lyrics model for AI-generated and user-edited lyrics.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Lyrics(Base):
    """Lyrics model for generated and edited song lyrics."""
    
    __tablename__ = "lyrics"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True)
    theme = Column(Text)
    generated_lyrics = Column(Text, nullable=False)
    edited_lyrics = Column(Text)
    structure = Column(JSON, default=dict)  # verses, chorus, bridge structure
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="lyrics")
