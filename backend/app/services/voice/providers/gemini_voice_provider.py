import logging
from typing import Dict, Any, Optional, Tuple
import google.genai as genai
from google.genai import types

from app.core.config import settings
from app.services.voice.base_stt import BaseSpeechToTextProvider
from app.services.voice.base_tts import BaseTextToSpeechProvider

logger = logging.getLogger("gemini_voice")

class GeminiSpeechToTextProvider(BaseSpeechToTextProvider):
    """Real Speech-to-Text Provider using Gemini."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        key = api_key or settings.GEMINI_API_KEY
        if not key:
            raise ValueError("GEMINI_API_KEY is not configured.")
        self.client = genai.Client(api_key=key)
        self.model = model or "gemini-3.8-flash"

    def transcribe(
        self, audio_bytes: bytes, language: Optional[str] = None
    ) -> Dict[str, Any]:
        """Transcribe audio bytes using Gemini API."""
        try:
            # We assume audio is somewhat standard (like wav, mp3, ogg, etc.)
            # We'll pass it as a generic audio MIME type, or we could pass the raw bytes.
            # Gemini models accept inline data for audio.
            
            # Since we don't know the exact MIME type here (it's validated upstream),
            # we'll use a generic one or infer it. For Gemini, 'audio/mp3' or 'audio/wav'
            # often works for most formats if the headers are correct. Let's just use 'audio/mp3'
            # or try to detect it. We can just use 'audio/mp3' for now as a fallback.
            # A better approach is to pass the mime type if possible, but the interface
            # doesn't take mime_type currently. Let's just use audio/mpeg as a general audio catchall.
            mime_type = "audio/mpeg"
            
            contents = [
                types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
                "Please transcribe the following audio accurately. Just output the transcription and nothing else.",
            ]
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
            )
            
            text = response.text or ""
            
            return {
                "text": text.strip(),
                "language": language or "en-IN",
                "duration_seconds": max(1, len(audio_bytes) // 16000),  # Rough estimate
                "confidence": None,
            }
        except Exception as e:
            logger.error(f"Gemini STT failed: {e}", exc_info=True)
            raise RuntimeError(f"Failed to transcribe audio: {e}")


class GeminiTextToSpeechProvider(BaseTextToSpeechProvider):
    """Real Text-to-Speech Provider using Gemini."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        key = api_key or settings.GEMINI_API_KEY
        if not key:
            raise ValueError("GEMINI_API_KEY is not configured.")
        self.client = genai.Client(api_key=key)
        self.model = model or "gemini-3.8-flash"

    def synthesize(
        self, text: str, voice: Optional[str] = None, language: Optional[str] = None
    ) -> Tuple[bytes, str]:
        """Synthesize text into speech audio bytes using Gemini API."""
        try:
            voice_name = voice or "Aoede" # Aoede, Puck, Charon, Kore, Fenrir, Puma
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=text,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice_name
                            )
                        )
                    )
                )
            )
            
            if not response.candidates or not response.candidates[0].content.parts:
                raise RuntimeError("No audio data returned from Gemini TTS.")
                
            part = response.candidates[0].content.parts[0]
            if not hasattr(part, 'inline_data') or not part.inline_data:
                raise RuntimeError("Missing inline_data in Gemini TTS response.")
                
            audio_bytes = part.inline_data.data
            mime_type = part.inline_data.mime_type
            
            return audio_bytes, mime_type
        except Exception as e:
            logger.error(f"Gemini TTS failed: {e}", exc_info=True)
            raise RuntimeError(f"Failed to synthesize speech: {e}")
