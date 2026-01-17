"""
Lyrics generation and management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.api.v1.auth import get_current_user
from pydantic import BaseModel

router = APIRouter()


class GenerateLyricsRequest(BaseModel):
    """Request model for lyric generation."""
    theme: str
    emotion: str = None
    project_id: int = None


@router.post("/lyrics/generate")
async def generate_lyrics(
    request: GenerateLyricsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate lyrics from theme using Gemini."""
    # TODO: Implement Gemini text generation
    return {"message": "Lyric generation endpoint - to be implemented"}


@router.post("/lyrics/match")
async def match_lyrics(
    lyrics_id: int,
    melody_url: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Match lyrics to melody."""
    # TODO: Implement lyric matching
    return {"message": "Lyric matching endpoint - to be implemented"}


@router.put("/lyrics/{lyrics_id}")
async def update_lyrics(
    lyrics_id: int,
    edited_lyrics: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update lyrics."""
    # TODO: Implement lyric update
    return {"message": "Update lyrics endpoint - to be implemented"}
