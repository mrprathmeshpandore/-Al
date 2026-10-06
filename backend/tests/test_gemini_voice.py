import pytest
from unittest.mock import MagicMock, patch
from app.services.voice.providers.gemini_voice_provider import GeminiSpeechToTextProvider, GeminiTextToSpeechProvider
from google.genai.errors import APIError

class MockGenAIClient:
    def __init__(self, *args, **kwargs):
        self.models = MagicMock()

@pytest.fixture
def gemini_stt():
    with patch("app.services.voice.providers.gemini_voice_provider.genai.Client", MockGenAIClient):
        return GeminiSpeechToTextProvider(api_key="fake-key")

@pytest.fixture
def gemini_tts():
    with patch("app.services.voice.providers.gemini_voice_provider.genai.Client", MockGenAIClient):
        return GeminiTextToSpeechProvider(api_key="fake-key")

def test_stt_success(gemini_stt):
    mock_response = MagicMock()
    mock_response.text = "This is a transcribed text."
    gemini_stt.client.models.generate_content.return_value = mock_response
    
    result = gemini_stt.transcribe(b"dummy_audio_bytes")
    
    assert result["text"] == "This is a transcribed text."
    assert result["language"] == "en-IN"
    gemini_stt.client.models.generate_content.assert_called_once()

def test_stt_gemini_failure(gemini_stt):
    # Simulate 502/503 failure
    gemini_stt.client.models.generate_content.side_effect = Exception("Service Unavailable")
    
    with pytest.raises(RuntimeError) as exc:
        gemini_stt.transcribe(b"dummy_audio_bytes")
    assert "Failed to transcribe audio" in str(exc.value)

def test_stt_rate_limit(gemini_stt):
    # Simulate 429 rate limit
    gemini_stt.client.models.generate_content.side_effect = Exception("Rate Limit Exceeded")
    
    with pytest.raises(RuntimeError) as exc:
        gemini_stt.transcribe(b"dummy_audio_bytes")
    assert "Failed to transcribe audio" in str(exc.value)

def test_stt_timeout(gemini_stt):
    # Simulate timeout
    import requests
    gemini_stt.client.models.generate_content.side_effect = requests.exceptions.Timeout("Connection timed out")
    
    with pytest.raises(RuntimeError) as exc:
        gemini_stt.transcribe(b"dummy_audio_bytes")
    assert "Failed to transcribe audio" in str(exc.value)

def test_tts_success(gemini_tts):
    mock_response = MagicMock()
    mock_part = MagicMock()
    mock_part.inline_data.data = b"synthetic_audio_bytes"
    mock_part.inline_data.mime_type = "audio/mpeg"
    mock_response.candidates = [MagicMock(content=MagicMock(parts=[mock_part]))]
    
    gemini_tts.client.models.generate_content.return_value = mock_response
    
    audio_bytes, mime_type = gemini_tts.synthesize("Hello world")
    
    assert audio_bytes == b"synthetic_audio_bytes"
    assert mime_type == "audio/mpeg"
    gemini_tts.client.models.generate_content.assert_called_once()

def test_tts_gemini_failure(gemini_tts):
    gemini_tts.client.models.generate_content.side_effect = Exception("Service Unavailable")
    with patch("gtts.gTTS", side_effect=Exception("gTTS Unavailable")):
        with pytest.raises(RuntimeError) as exc:
            gemini_tts.synthesize("Hello world")
        assert "Failed to synthesize speech" in str(exc.value)

def test_tts_rate_limit(gemini_tts):
    gemini_tts.client.models.generate_content.side_effect = Exception("Rate Limit Exceeded")
    with patch("gtts.gTTS", side_effect=Exception("gTTS Unavailable")):
        with pytest.raises(RuntimeError) as exc:
            gemini_tts.synthesize("Hello world")
        assert "Failed to synthesize speech" in str(exc.value)

def test_tts_timeout(gemini_tts):
    import requests
    gemini_tts.client.models.generate_content.side_effect = requests.exceptions.Timeout("Connection timed out")
    with patch("gtts.gTTS", side_effect=Exception("gTTS Unavailable")):
        with pytest.raises(RuntimeError) as exc:
            gemini_tts.synthesize("Hello world")
        assert "Failed to synthesize speech" in str(exc.value)
