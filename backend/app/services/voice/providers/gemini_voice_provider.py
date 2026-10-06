import logging
import io
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
        self.model = model or getattr(settings, 'GEMINI_GENERATION_MODEL', None) or "gemini-flash-lite-latest"

    def transcribe(
        self, audio_bytes: bytes, language: Optional[str] = None, mime_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Transcribe audio bytes using Gemini API with automatic fallback models."""
        target_mime = mime_type or "audio/wav"
        if ";" in target_mime:
            target_mime = target_mime.split(";")[0].strip()

        contents = [
            types.Part.from_bytes(data=audio_bytes, mime_type=target_mime),
            "Transcribe spoken audio verbatim.",
        ]

        config = types.GenerateContentConfig(
            temperature=0.0,
            system_instruction=(
                "You are an expert verbatim Speech-to-Text transcription engine for candidate interview answers.\n"
                "Instructions:\n"
                "1. Transcribe EXACTLY and WORD-FOR-WORD what the candidate speaks in their audio recording (in Marathi, Marathi-English, English, or Hindi).\n"
                "2. DO NOT paraphrase, guess, alter, summarize, or invent different words or questions.\n"
                "3. DO NOT hallucinate numbers or random words if the audio is silent or low volume.\n"
                "4. If no clear spoken words are heard, output nothing (empty string)."
            )
        )

        candidate_models = [self.model, "gemini-flash-lite-latest", "gemini-2.5-flash", "gemini-1.5-flash"]
        candidate_models = list(dict.fromkeys(candidate_models))

        last_error = None
        for current_model in candidate_models:
            try:
                response = self.client.models.generate_content(
                    model=current_model,
                    contents=contents,
                    config=config,
                )
                text = response.text or ""
                return {
                    "text": text.strip(),
                    "language": language or "en-IN",
                    "duration_seconds": max(1, len(audio_bytes) // 16000),
                    "confidence": None,
                }
            except Exception as e:
                logger.warning(f"Gemini STT model '{current_model}' failed: {e}. Trying fallback...")
                last_error = e

        logger.error(f"All Gemini STT fallback models failed: {last_error}", exc_info=True)
        raise RuntimeError(f"Failed to transcribe audio: {last_error}")


class GeminiTextToSpeechProvider(BaseTextToSpeechProvider):
    """Real Text-to-Speech Provider using Gemini with gTTS fallback."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        key = api_key or settings.GEMINI_API_KEY
        if not key:
            raise ValueError("GEMINI_API_KEY is not configured.")
        self.client = genai.Client(api_key=key)
        self.model = model or getattr(settings, 'GEMINI_GENERATION_MODEL', None) or "gemini-flash-lite-latest"

    def _gtts_fallback(self, text: str, language: Optional[str] = None) -> Tuple[bytes, str]:
        """Fallback TTS using Google Text-to-Speech (gTTS) for English, Marathi, Hindi with natural Indian accent."""
        try:
            from gtts import gTTS
            lang_code = "en"
            if language:
                clean_lang = language.lower()
                if "mr" in clean_lang or "marathi" in clean_lang:
                    lang_code = "mr"
                elif "hi" in clean_lang or "hindi" in clean_lang:
                    lang_code = "hi"
            tts = gTTS(text=text, lang=lang_code, tld="co.in")
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            return fp.getvalue(), "audio/mpeg"
        except Exception as e:
            logger.error(f"gTTS fallback failed: {e}")
            raise RuntimeError(f"Failed to synthesize speech: {e}") from e

    def synthesize(
        self, text: str, voice: Optional[str] = None, language: Optional[str] = None
    ) -> Tuple[bytes, str]:
        """Synthesize text into speech audio bytes using Gemini API with gTTS fallback."""
        default_voice = getattr(settings, "VOICE_DEFAULT_VOICE", "Kore")
        if not default_voice or default_voice.lower() == "default":
            default_voice = "Kore"
        voice_name = voice if (voice and voice.lower() != "default") else default_voice

        system_instruction = (
            "You are a calm, mature, and highly professional female UPSC Interview Board Member.\n"
            "Speak the candidate question with natural human conversational pacing, clear native pronunciation,\n"
            "dignified sentence rhythm, and medium speaking speed with appropriate sentence-level pauses.\n"
            "Do not sound robotic, artificial, dramatic, cartoonish, or overly emotional."
        )

        candidate_models = [self.model, "gemini-flash-lite-latest", "gemini-2.5-flash", "gemini-1.5-flash"]
        candidate_models = list(dict.fromkeys(candidate_models))

        last_error = None
        for current_model in candidate_models:
            try:
                response = self.client.models.generate_content(
                    model=current_model,
                    contents=text,
                    config=types.GenerateContentConfig(
                        response_modalities=["AUDIO"],
                        system_instruction=system_instruction,
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
                    continue
                part = response.candidates[0].content.parts[0]
                if not hasattr(part, 'inline_data') or not part.inline_data:
                    continue
                audio_bytes = part.inline_data.data
                mime_type = part.inline_data.mime_type
                return audio_bytes, mime_type
            except Exception as e:
                logger.warning(f"Gemini TTS model '{current_model}' failed: {e}. Trying fallback...")
                last_error = e

        # Fall back to gTTS if Gemini audio modality is unavailable
        logger.info(f"All Gemini models failed/lacked audio modality ({last_error}). Triggering gTTS fallback...")
        return self._gtts_fallback(text=text, language=language)

