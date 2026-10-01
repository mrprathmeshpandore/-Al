from abc import ABC, abstractmethod
from typing import Tuple, Optional


class BaseTextToSpeechProvider(ABC):
    """Abstract Base Class for Text-to-Speech Providers."""

    @abstractmethod
    def synthesize(
        self, text: str, voice: Optional[str] = None, language: Optional[str] = None
    ) -> Tuple[bytes, str]:
        """
        Synthesize text into speech audio bytes.

        Returns:
            Tuple of (audio_bytes, media_type) e.g. (b"...", "audio/mpeg")
        """
        pass
