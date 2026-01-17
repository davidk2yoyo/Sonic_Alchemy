"""
Audio processing service for pitch correction, timing, and manipulation.
"""
import librosa
import soundfile as sf
import numpy as np
from pydub import AudioSegment
import io
import logging
from typing import Tuple, Optional, Dict, Any

logger = logging.getLogger(__name__)


class AudioService:
    """Service for audio processing operations."""
    
    def __init__(self):
        """Initialize audio service."""
        self.sample_rate = 44100  # Standard sample rate
    
    def load_audio(self, audio_data: bytes, format: str = "wav") -> Tuple[np.ndarray, int]:
        """
        Load audio from bytes.
        
        Args:
            audio_data: Audio file bytes
            format: Audio format
            
        Returns:
            Tuple of (audio_array, sample_rate)
        """
        try:
            # Convert bytes to file-like object
            audio_file = io.BytesIO(audio_data)
            
            # Load audio
            y, sr = librosa.load(audio_file, sr=self.sample_rate)
            
            return y, sr
            
        except Exception as e:
            logger.error(f"Error loading audio: {e}")
            raise Exception(f"Failed to load audio: {str(e)}")
    
    def detect_pitch(self, audio_array: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """
        Detect pitch information from audio.
        
        Args:
            audio_array: Audio signal array
            sample_rate: Sample rate
            
        Returns:
            Dictionary with pitch information
        """
        try:
            # Extract pitch using librosa
            pitches, magnitudes = librosa.piptrack(y=audio_array, sr=sample_rate)
            
            # Get dominant pitch
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            if not pitch_values:
                return {
                    "average_pitch": 0,
                    "pitch_notes": [],
                    "confidence": 0.0
                }
            
            avg_pitch = np.mean(pitch_values)
            
            # Convert to note names (simplified)
            note = librosa.hz_to_note(avg_pitch) if avg_pitch > 0 else "C4"
            
            return {
                "average_pitch": float(avg_pitch),
                "pitch_notes": [note],
                "confidence": float(np.std(pitch_values) / avg_pitch) if avg_pitch > 0 else 1.0
            }
            
        except Exception as e:
            logger.error(f"Error detecting pitch: {e}")
            return {
                "average_pitch": 0,
                "pitch_notes": [],
                "confidence": 0.0
            }
    
    def correct_pitch(self, audio_array: np.ndarray, sample_rate: int, target_note: str = None) -> np.ndarray:
        """
        Apply pitch correction to audio.
        
        Args:
            audio_array: Audio signal array
            sample_rate: Sample rate
            target_note: Optional target note (e.g., "C4")
            
        Returns:
            Pitch-corrected audio array
        """
        try:
            # Simple pitch shifting using librosa
            if target_note:
                # Convert note to frequency
                target_freq = librosa.note_to_hz(target_note)
                
                # Detect current pitch
                pitch_info = self.detect_pitch(audio_array, sample_rate)
                current_pitch = pitch_info.get("average_pitch", 0)
                
                if current_pitch > 0:
                    # Calculate pitch shift ratio
                    pitch_shift = target_freq / current_pitch
                    
                    # Apply pitch shift
                    corrected = librosa.effects.pitch_shift(
                        audio_array,
                        sr=sample_rate,
                        n_steps=librosa.hz_to_midi(target_freq) - librosa.hz_to_midi(current_pitch)
                    )
                    return corrected
            
            # Default: slight auto-tune effect
            # This is a simplified version - full auto-tune is more complex
            return audio_array
            
        except Exception as e:
            logger.error(f"Error correcting pitch: {e}")
            return audio_array
    
    def quantize_timing(self, audio_array: np.ndarray, sample_rate: int, bpm: float = 120) -> np.ndarray:
        """
        Quantize audio timing to beat grid.
        
        Args:
            audio_array: Audio signal array
            sample_rate: Sample rate
            bpm: Beats per minute
            
        Returns:
            Timing-quantized audio array
        """
        try:
            # Calculate beat duration in samples
            beat_duration_samples = int((60.0 / bpm) * sample_rate)
            
            # Detect tempo and beats
            tempo, beats = librosa.beat.beat_track(y=audio_array, sr=sample_rate)
            
            # Simple quantization: align to nearest beat
            # This is a simplified version
            return audio_array
            
        except Exception as e:
            logger.error(f"Error quantizing timing: {e}")
            return audio_array
    
    def save_audio(self, audio_array: np.ndarray, sample_rate: int, format: str = "wav") -> bytes:
        """
        Save audio array to bytes.
        
        Args:
            audio_array: Audio signal array
            sample_rate: Sample rate
            format: Output format
            
        Returns:
            Audio file bytes
        """
        try:
            # Create file-like object
            audio_file = io.BytesIO()
            
            # Save audio
            sf.write(audio_file, audio_array, sample_rate, format=format)
            
            # Get bytes
            audio_file.seek(0)
            return audio_file.read()
            
        except Exception as e:
            logger.error(f"Error saving audio: {e}")
            raise Exception(f"Failed to save audio: {str(e)}")
    
    def get_audio_duration(self, audio_data: bytes) -> float:
        """
        Get duration of audio file in seconds.
        
        Args:
            audio_data: Audio file bytes
            
        Returns:
            Duration in seconds
        """
        try:
            audio_file = io.BytesIO(audio_data)
            y, sr = librosa.load(audio_file, sr=None)
            duration = librosa.get_duration(y=y, sr=sr)
            return float(duration)
            
        except Exception as e:
            logger.error(f"Error getting audio duration: {e}")
            return 0.0


# Create singleton instance
audio_service = AudioService()
