"""
Lyrics generation and management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.lyrics import Lyrics
from app.models.project import Project
from app.api.v1.auth import get_current_user
from app.services.gemini_service import gemini_service
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class GenerateLyricsRequest(BaseModel):
    """Request model for lyric generation."""
    theme: str
    emotion: Optional[str] = None
    style: Optional[str] = None
    project_id: Optional[int] = None


class LyricsResponse(BaseModel):
    """Lyrics response model."""
    id: int
    theme: Optional[str]
    generated_lyrics: str
    edited_lyrics: Optional[str]
    structure: dict
    created_at: str
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj: Lyrics):
        """Convert Lyrics model to response."""
        return cls(
            id=obj.id,
            theme=obj.theme,
            generated_lyrics=obj.generated_lyrics,
            edited_lyrics=obj.edited_lyrics,
            structure=obj.structure or {},
            created_at=obj.created_at.isoformat() if obj.created_at else ""
        )


class UpdateLyricsRequest(BaseModel):
    """Request model for updating lyrics."""
    edited_lyrics: str


@router.post("/lyrics/generate", response_model=LyricsResponse, status_code=status.HTTP_201_CREATED)
async def generate_lyrics(
    request: GenerateLyricsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate lyrics from theme using Gemini."""
    # Verify project access if project_id provided
    if request.project_id:
        project = db.query(Project).filter(
            Project.id == request.project_id,
            Project.user_id == current_user.id
        ).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
    
    # Generate lyrics using Gemini
    try:
        result = gemini_service.generate_lyrics(
            theme=request.theme,
            emotion=request.emotion,
            style=request.style
        )
    except Exception as e:
        error_str = str(e)
        # Check for quota/rate limit errors
        if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="You exceeded your current quota, please check your plan and billing"
            )
        elif "403" in error_str or "permission" in error_str.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="API key permission denied. Please check your Gemini API key."
            )
        elif "401" in error_str or "unauthorized" in error_str.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key. Please check your GEMINI_API_KEY in .env"
            )
        elif "503" in error_str or "service unavailable" in error_str.lower():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service temporarily unavailable. Please try again later."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate lyrics: {error_str}"
            )
    
    # Create lyrics record
    lyrics = Lyrics(
        project_id=request.project_id,
        theme=request.theme,
        generated_lyrics=result["lyrics"],
        structure=result["structure"]
    )
    
    db.add(lyrics)
    db.commit()
    db.refresh(lyrics)
    
    # Convert to response model
    return LyricsResponse.from_orm(lyrics)


@router.post("/lyrics/match")
async def match_lyrics(
    lyrics_id: int,
    melody_url: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Match lyrics to melody."""
    # Get lyrics
    lyrics = db.query(Lyrics).filter(Lyrics.id == lyrics_id).first()
    
    if not lyrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lyrics not found"
        )
    
    # Check access
    if lyrics.project_id:
        project = db.query(Project).filter(Project.id == lyrics.project_id).first()
        if project and project.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    # For MVP, return the lyrics as-is
    # Full implementation would analyze melody and adjust lyrics
    # TODO: Implement melody analysis and lyric matching
    
    return {
        "lyrics_id": lyrics_id,
        "matched_lyrics": lyrics.generated_lyrics,
        "message": "Lyric matching completed (simplified for MVP)"
    }


@router.put("/lyrics/{lyrics_id}", response_model=LyricsResponse)
async def update_lyrics(
    lyrics_id: int,
    request: UpdateLyricsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update lyrics."""
    # Get lyrics
    lyrics = db.query(Lyrics).filter(Lyrics.id == lyrics_id).first()
    
    if not lyrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lyrics not found"
        )
    
    # Check access
    if lyrics.project_id:
        project = db.query(Project).filter(Project.id == lyrics.project_id).first()
        if project and project.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    # Update lyrics
    lyrics.edited_lyrics = request.edited_lyrics
    db.commit()
    db.refresh(lyrics)
    
    return lyrics
