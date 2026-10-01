from typing import Dict, Any, Optional, Tuple
from app.services.voice.base_stt import BaseSpeechToTextProvider
from app.services.voice.base_tts import BaseTextToSpeechProvider


class FakeSpeechToTextProvider(BaseSpeechToTextProvider):
    """Mock Speech-to-Text Provider for testing and local development without external API dependencies."""

    def __init__(self, default_text: Optional[str] = None, fail_mode: bool = False):
        self.default_text = default_text
        self.fail_mode = fail_mode

    def transcribe(
        self, audio_bytes: bytes, language: Optional[str] = None
    ) -> Dict[str, Any]:
        if self.fail_mode:
            raise RuntimeError("STT provider failure simulated.")

        if not audio_bytes:
            return {
                "text": "",
                "language": language or "en-IN",
                "duration_seconds": 0,
                "confidence": None,
            }

        # Estimate duration based on byte size assuming ~16KB per sec
        estimated_duration = max(1, min(180, int(len(audio_bytes) / 16000)))

        text = (
            self.default_text
            or "India's federal structure ensures dynamic balance between central authority and state autonomy in governance and policy implementation."
        )

        return {
            "text": text,
            "language": language or "en-IN",
            "duration_seconds": estimated_duration,
            "confidence": None,
        }


class FakeTextToSpeechProvider(BaseTextToSpeechProvider):
    """Mock Text-to-Speech Provider returning valid synthetic audio bytes."""

    def __init__(self, fail_mode: bool = False):
        self.fail_mode = fail_mode

    def synthesize(
        self, text: str, voice: Optional[str] = None, language: Optional[str] = None
    ) -> Tuple[bytes, str]:
        if self.fail_mode:
            raise RuntimeError("TTS provider failure simulated.")

        # Minimal valid MP3 sync header + frame data for testing / playback
        # 128 bytes MP3 audio stream mock
        mp3_header = b"\xff\xfb\x90\x44\x00\x00\x00\x00\x00\x00\x00\x00"
        audio_payload = mp3_header + (b"\x00" * 200)

        return audio_payload, "audio/mpeg"
