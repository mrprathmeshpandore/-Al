from typing import Optional
from pydantic import BaseModel, Field


class VoiceTranscribeResponse(BaseModel):
    """Schema for audio transcription response."""
    text: str = Field(..., description="Transcribed text content")
    language: str = Field(default="en-IN", description="Detected or specified audio language")
    duration_seconds: Optional[float] = Field(default=None, description="Audio duration in seconds")
    confidence: Optional[float] = Field(default=None, description="Transcription confidence score (null if unavailable)")


class VoiceSynthesizeRequest(BaseModel):
    """Schema for text-to-speech synthesis request."""
    text: str = Field(..., min_length=1, description="Text string to synthesize into audio")
    language: Optional[str] = Field(default="en-IN", description="Target voice language code")
    voice: Optional[str] = Field(default="default", description="Voice accent or model name")
