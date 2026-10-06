import logging
import os
import tempfile
from typing import Dict, Any, Optional
from fastapi import HTTPException, status

from app.core.config import Settings
from app.services.voice.base_stt import BaseSpeechToTextProvider
from app.services.voice.providers.fake_voice_provider import FakeSpeechToTextProvider

logger = logging.getLogger("stt_service")


ALLOWED_MIME_TYPES = {
    "audio/wav",
    "audio/x-wav",
    "audio/mp3",
    "audio/mpeg",
    "audio/webm",
    "audio/ogg",
    "audio/m4a",
    "audio/x-m4a",
    "audio/mp4",
}

ALLOWED_EXTENSIONS = {".wav", ".mp3", ".webm", ".ogg", ".m4a", ".mp4"}


class SpeechToTextService:
    """High-level STT Service enforcing audio security, validation, and provider dispatch."""

    def __init__(self, provider: Optional[BaseSpeechToTextProvider] = None, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self.provider = provider or self._resolve_provider()

    def _resolve_provider(self) -> BaseSpeechToTextProvider:
        provider_name = (self.settings.VOICE_STT_PROVIDER or "fake").lower()
        if provider_name in ("gemini", "google"):
            try:
                from app.services.voice.providers.gemini_voice_provider import GeminiSpeechToTextProvider
                return GeminiSpeechToTextProvider()
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini STT provider ({e}); falling back to FakeSpeechToTextProvider.")
                return FakeSpeechToTextProvider()
        return FakeSpeechToTextProvider()

    def transcribe_audio(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not file_bytes:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Audio file content is empty.",
            )

        max_size_bytes = self.settings.VOICE_MAX_AUDIO_SIZE_MB * 1024 * 1024
        if len(file_bytes) > max_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Audio file size exceeds maximum limit of {self.settings.VOICE_MAX_AUDIO_SIZE_MB} MB.",
            )

        # Validate MIME type and file extension
        ext = os.path.splitext(filename or "")[1].lower()
        clean_content_type = (content_type or "").split(";")[0].strip().lower()

        if clean_content_type not in ALLOWED_MIME_TYPES or ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported audio format '{clean_content_type}' or extension '{ext}'.",
            )

        # Secure Temporary File Processing
        temp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=ext or ".wav", delete=False) as tmp:
                tmp.write(file_bytes)
                temp_file_path = tmp.name

            target_language = language or self.settings.VOICE_DEFAULT_LANGUAGE
            result = self.provider.transcribe(file_bytes, language=target_language, mime_type=clean_content_type)
            return result

        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Voice transcription provider error: {err}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Voice transcription provider error: {str(err)}",
            )
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except OSError:
                    pass
