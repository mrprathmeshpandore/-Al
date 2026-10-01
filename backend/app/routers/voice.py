from typing import Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile, Response, status
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.voice import VoiceTranscribeResponse, VoiceSynthesizeRequest
from app.services.voice.stt_service import SpeechToTextService
from app.services.voice.tts_service import TextToSpeechService

router = APIRouter(prefix="/voice", tags=["Voice Engine"])


@router.post("/transcribe", response_model=VoiceTranscribeResponse)
async def transcribe_audio_endpoint(
    audio: UploadFile = File(...),
    language: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
):
    """
    Transcribe uploaded candidate audio recording into canonical text transcript.
    Requires authentication. Strictly enforces audio file format and size limits.
    """
    file_bytes = await audio.read()
    stt_service = SpeechToTextService()
    
    result = stt_service.transcribe_audio(
        file_bytes=file_bytes,
        filename=audio.filename or "recording.wav",
        content_type=audio.content_type or "audio/wav",
        language=language,
    )
    
    return VoiceTranscribeResponse(
        text=result.get("text", ""),
        language=result.get("language", language or "en-IN"),
        duration_seconds=result.get("duration_seconds"),
        confidence=result.get("confidence"),
    )


@router.post("/synthesize")
def synthesize_speech_endpoint(
    req: VoiceSynthesizeRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Synthesize text question into audio speech stream.
    Requires authentication. Returns binary audio response stream.
    """
    tts_service = TextToSpeechService()
    audio_bytes, media_type = tts_service.synthesize_speech(
        text=req.text,
        voice=req.voice,
        language=req.language,
    )
    
    return Response(
        content=audio_bytes,
        media_type=media_type,
        headers={
            "Content-Disposition": "inline; filename=synthesized_question.mp3",
            "Cache-Control": "no-cache",
        },
    )
