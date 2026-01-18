"""
Gemini API service for Vision, Audio, and Text generation.
Handles all interactions with Google Gemini API.
"""
import google.generativeai as genai
from app.core.config import settings
import base64
import json
import time
from typing import Dict, Optional, Any
from functools import lru_cache
import redis
import logging

logger = logging.getLogger(__name__)

# Configure Gemini API - ensure it's loaded from env
def _configure_gemini():
    """Configure Gemini API with API key from settings."""
    api_key = settings.GEMINI_API_KEY
    if not api_key or len(api_key) < 20:
        # Try loading from environment directly
        import os
        from dotenv import load_dotenv
        from pathlib import Path
        env_path = Path(__file__).parent.parent.parent.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path, override=True)
            api_key = os.getenv('GEMINI_API_KEY') or settings.GEMINI_API_KEY
    
    if api_key and len(api_key) > 20:
        genai.configure(api_key=api_key)
        logger.info("Gemini API configured successfully")
    else:
        logger.warning("GEMINI_API_KEY not found or invalid")

# Configure on module load
_configure_gemini()

# Redis client for caching (if enabled)
redis_client = None
if settings.GEMINI_CACHE_ENABLED:
    try:
        import redis
        redis_client = redis.from_url(settings.REDIS_URL)
    except Exception as e:
        logger.warning(f"Redis not available for caching: {e}")


class GeminiService:
    """Service for interacting with Gemini API."""
    
    def __init__(self):
        """Initialize Gemini service with models."""
        self.vision_model = genai.GenerativeModel(settings.GEMINI_MODEL_VISION)
        self.text_model = genai.GenerativeModel(settings.GEMINI_MODEL_TEXT)
        self.audio_model = genai.GenerativeModel(settings.GEMINI_MODEL_AUDIO)
        self.rate_limit_delay = 60 / settings.GEMINI_RATE_LIMIT  # Delay between requests
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Apply rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _get_cache_key(self, cache_type: str, identifier: str) -> str:
        """Generate cache key."""
        return f"gemini:{cache_type}:{identifier}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Get value from cache."""
        if not settings.GEMINI_CACHE_ENABLED or not redis_client:
            return None
        
        try:
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache read error: {e}")
        
        return None
    
    def _set_cache(self, cache_key: str, value: Dict, ttl: int = 3600):
        """Set value in cache."""
        if not settings.GEMINI_CACHE_ENABLED or not redis_client:
            return
        
        try:
            redis_client.setex(
                cache_key,
                ttl,
                json.dumps(value)
            )
        except Exception as e:
            logger.warning(f"Cache write error: {e}")
    
    def analyze_image_emotion(self, image_data: bytes, image_hash: str = None) -> Dict[str, Any]:
        """
        Analyze image emotion using Gemini Vision API.
        
        Args:
            image_data: Image file bytes
            image_hash: Optional hash for caching
            
        Returns:
            Dictionary with emotion analysis results
        """
        # Check cache
        if image_hash:
            cache_key = self._get_cache_key("emotion", image_hash)
            cached = self._get_from_cache(cache_key)
            if cached:
                logger.info("Returning cached emotion analysis")
                return cached
        
        # Rate limiting
        self._rate_limit()
        
        try:
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Create prompt for emotion analysis
            prompt = """
            Analyze this image and identify the primary emotions it conveys.
            Consider colors, composition, subject matter, and overall mood.
            
            Provide your analysis in the following JSON format:
            {
                "primary_emotion": "emotion_name",
                "secondary_emotions": ["emotion1", "emotion2"],
                "confidence": 0.0-1.0,
                "color_analysis": "description",
                "mood_description": "detailed description",
                "music_suggestions": {
                    "genre": "suggested_genre",
                    "tempo": "slow/medium/fast",
                    "instruments": ["instrument1", "instrument2"]
                }
            }
            """
            
            # Call Gemini Vision API
            response = self.vision_model.generate_content([
                prompt,
                {
                    "mime_type": "image/jpeg",
                    "data": image_base64
                }
            ])
            
            # Parse response
            result_text = response.text
            
            # Try to extract JSON from response
            try:
                # Find JSON in response
                json_start = result_text.find('{')
                json_end = result_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    result_json = json.loads(result_text[json_start:json_end])
                else:
                    # Fallback: create structured response from text
                    result_json = {
                        "primary_emotion": "unknown",
                        "secondary_emotions": [],
                        "confidence": 0.5,
                        "raw_analysis": result_text,
                        "music_suggestions": {
                            "genre": "ambient",
                            "tempo": "medium",
                            "instruments": []
                        }
                    }
            except json.JSONDecodeError:
                # Fallback response
                result_json = {
                    "primary_emotion": "unknown",
                    "secondary_emotions": [],
                    "confidence": 0.5,
                    "raw_analysis": result_text,
                    "music_suggestions": {
                        "genre": "ambient",
                        "tempo": "medium",
                        "instruments": []
                    }
                }
            
            # Cache result
            if image_hash:
                self._set_cache(cache_key, result_json, ttl=settings.CACHE_TTL)
            
            return result_json
            
        except Exception as e:
            logger.error(f"Error analyzing image emotion: {e}")
            raise Exception(f"Failed to analyze image emotion: {str(e)}")
    
    def generate_lyrics(self, theme: str, emotion: str = None, style: str = None) -> Dict[str, Any]:
        """
        Generate lyrics using Gemini Text API.
        
        Args:
            theme: Theme or topic for lyrics
            emotion: Optional emotion to convey
            style: Optional style (e.g., "ballad", "upbeat")
            
        Returns:
            Dictionary with generated lyrics and structure
        """
        # Create cache key
        cache_key = self._get_cache_key("lyrics", f"{theme}:{emotion}:{style}")
        cached = self._get_from_cache(cache_key)
        if cached:
            logger.info("Returning cached lyrics")
            return cached
        
        # Rate limiting
        self._rate_limit()
        
        try:
            # Build prompt
            prompt = f"""Generate song lyrics based on the following:
            
Theme: {theme}
{f'Emotion: {emotion}' if emotion else ''}
{f'Style: {style}' if style else ''}

Create a complete song with:
- 2-3 verses
- A catchy chorus (repeated 2-3 times)
- Optional bridge

Format the lyrics clearly with verse, chorus, and bridge labels.
Make the lyrics emotional, poetic, and suitable for music.
"""
            
            # Call Gemini Text API
            response = self.text_model.generate_content(prompt)
            lyrics_text = response.text
            
            # Parse structure
            structure = self._parse_lyrics_structure(lyrics_text)
            
            result = {
                "lyrics": lyrics_text,
                "structure": structure,
                "theme": theme,
                "emotion": emotion,
                "style": style
            }
            
            # Cache result
            self._set_cache(cache_key, result, ttl=settings.CACHE_TTL)
            
            return result
            
        except Exception as e:
            error_str = str(e)
            logger.error(f"Error generating lyrics: {e}")
            
            # Check for specific Gemini API errors
            if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
                raise Exception("429: You exceeded your current quota, please check your plan and billing")
            elif "403" in error_str or "permission" in error_str.lower():
                raise Exception("403: API key permission denied. Please check your Gemini API key.")
            elif "401" in error_str or "unauthorized" in error_str.lower():
                raise Exception("401: Invalid API key. Please check your GEMINI_API_KEY in .env")
            else:
                raise Exception(f"Failed to generate lyrics: {error_str}")
    
    def _parse_lyrics_structure(self, lyrics_text: str) -> Dict[str, Any]:
        """Parse lyrics text to extract structure."""
        structure = {
            "verses": [],
            "chorus": None,
            "bridge": None
        }
        
        lines = lyrics_text.split('\n')
        current_section = None
        
        for line in lines:
            line_lower = line.lower().strip()
            if 'verse' in line_lower or 'verse 1' in line_lower:
                current_section = 'verse'
            elif 'chorus' in line_lower:
                current_section = 'chorus'
            elif 'bridge' in line_lower:
                current_section = 'bridge'
            elif line.strip() and current_section:
                if current_section == 'verse':
                    structure['verses'].append(line.strip())
                elif current_section == 'chorus':
                    if not structure['chorus']:
                        structure['chorus'] = []
                    structure['chorus'].append(line.strip())
                elif current_section == 'bridge':
                    if not structure['bridge']:
                        structure['bridge'] = []
                    structure['bridge'].append(line.strip())
        
        return structure
    
    def transcribe_audio(self, audio_data: bytes, audio_format: str = "wav") -> Dict[str, Any]:
        """
        Transcribe audio using Gemini Audio API.
        
        Args:
            audio_data: Audio file bytes
            audio_format: Audio format (wav, mp3, etc.)
            
        Returns:
            Dictionary with transcription and analysis
        """
        # Rate limiting
        self._rate_limit()
        
        try:
            # Encode audio to base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # Determine MIME type
            mime_type_map = {
                "wav": "audio/wav",
                "mp3": "audio/mpeg",
                "m4a": "audio/mp4",
                "ogg": "audio/ogg"
            }
            mime_type = mime_type_map.get(audio_format.lower(), "audio/wav")
            
            prompt = """
            Transcribe this audio and analyze:
            1. The lyrics or spoken words
            2. The emotional tone
            3. The musical style (if any)
            4. Key themes or topics
            
            Provide a detailed transcription and analysis.
            """
            
            # Call Gemini Audio API
            response = self.audio_model.generate_content([
                prompt,
                {
                    "mime_type": mime_type,
                    "data": audio_base64
                }
            ])
            
            result = {
                "transcription": response.text,
                "audio_format": audio_format
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise Exception(f"Failed to transcribe audio: {str(e)}")
    
    def generate_music_prompt(self, emotion_analysis: Dict[str, Any]) -> str:
        """
        Generate music generation prompt from emotion analysis.
        
        Args:
            emotion_analysis: Emotion analysis results from image
            
        Returns:
            Music generation prompt string
        """
        primary_emotion = emotion_analysis.get("primary_emotion", "neutral")
        mood = emotion_analysis.get("mood_description", "")
        suggestions = emotion_analysis.get("music_suggestions", {})
        
        genre = suggestions.get("genre", "ambient")
        tempo = suggestions.get("tempo", "medium")
        instruments = suggestions.get("instruments", [])
        
        prompt = f"""Generate instrumental music with the following characteristics:
        
Emotion: {primary_emotion}
Mood: {mood}
Genre: {genre}
Tempo: {tempo}
Instruments: {', '.join(instruments) if instruments else 'synthesizer, piano'}

Create a {tempo} tempo {genre} track that conveys {primary_emotion} emotion.
The music should be suitable as a backing track for vocals.
Duration: 60 seconds.
"""
        
        return prompt


# Create singleton instance
gemini_service = GeminiService()
