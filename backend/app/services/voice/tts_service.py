from typing import Tuple, Optional
from fastapi import HTTPException, status

from app.core.config import Settings
from app.services.voice.base_tts import BaseTextToSpeechProvider
from app.services.voice.providers.fake_voice_provider import FakeTextToSpeechProvider


class TextToSpeechService:
    """High-level TTS Service enforcing input validation and provider dispatch."""

    def __init__(self, provider: Optional[BaseTextToSpeechProvider] = None, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self.provider = provider or self._resolve_provider()

    def _resolve_provider(self) -> BaseTextToSpeechProvider:
        provider_name = (self.settings.VOICE_TTS_PROVIDER or "fake").lower()
        if provider_name in ("gemini", "google", "gtts"):
            try:
                from app.services.voice.providers.gemini_voice_provider import GeminiTextToSpeechProvider
                return GeminiTextToSpeechProvider()
            except Exception as e:
                return FakeTextToSpeechProvider()
        return FakeTextToSpeechProvider()

    def synthesize_speech(
        self,
        text: str,
        voice: Optional[str] = None,
        language: Optional[str] = None,
    ) -> Tuple[bytes, str]:
        clean_text = (text or "").strip()
        if not clean_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Text to synthesize must not be empty.",
            )

        target_voice = voice or self.settings.VOICE_DEFAULT_VOICE
        target_language = language or self.settings.VOICE_DEFAULT_LANGUAGE

        try:
            return self.provider.synthesize(
                text=clean_text, voice=target_voice, language=target_language
            )
        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Voice TTS provider failure: {str(err)}",
            )
