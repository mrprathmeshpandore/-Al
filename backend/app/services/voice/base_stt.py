from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseSpeechToTextProvider(ABC):
    """Abstract Base Class for Speech-to-Text Providers."""

    @abstractmethod
    def transcribe(
        self, audio_bytes: bytes, language: Optional[str] = None, mime_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio bytes into structured output.

        Returns:
            Dict containing:
                "text": str,
                "language": str,
                "duration_seconds": Optional[float],
                "confidence": Optional[float] (null if provider does not supply)
        """
        pass
