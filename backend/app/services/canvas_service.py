"""
Canvas service for image handling and emotion analysis.
"""
import hashlib
from typing import Dict, Any, Optional
from app.services.gemini_service import gemini_service
import logging

logger = logging.getLogger(__name__)


class CanvasService:
    """Service for canvas operations."""
    
    def __init__(self):
        """Initialize canvas service."""
        pass
    
    def calculate_image_hash(self, image_data: bytes) -> str:
        """
        Calculate hash of image for caching.
        
        Args:
            image_data: Image file bytes
            
        Returns:
            SHA256 hash string
        """
        return hashlib.sha256(image_data).hexdigest()
    
    def analyze_emotion(self, image_data: bytes) -> Dict[str, Any]:
        """
        Analyze image emotion using Gemini Vision API.
        
        Args:
            image_data: Image file bytes
            
        Returns:
            Emotion analysis results
        """
        try:
            # Calculate hash for caching
            image_hash = self.calculate_image_hash(image_data)
            
            # Call Gemini service
            analysis = gemini_service.analyze_image_emotion(image_data, image_hash)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing emotion: {e}")
            raise
    
    def generate_music_prompt(self, emotion_analysis: Dict[str, Any]) -> str:
        """
        Generate music generation prompt from emotion analysis.
        
        Args:
            emotion_analysis: Emotion analysis results
            
        Returns:
            Music generation prompt
        """
        return gemini_service.generate_music_prompt(emotion_analysis)


# Create singleton instance
canvas_service = CanvasService()
