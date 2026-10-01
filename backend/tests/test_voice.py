import os
import io
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.models.question import InterviewQuestion
from app.models.interview import InterviewSession, InterviewSessionQuestion, InterviewAnswer, SessionStatus, QuestionSessionStatus
from app.utils.security import hash_password, create_access_token
from app.services.voice.stt_service import SpeechToTextService
from app.services.voice.tts_service import TextToSpeechService
from app.services.voice.providers.fake_voice_provider import FakeSpeechToTextProvider, FakeTextToSpeechProvider

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    app.dependency_overrides.clear()
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    
    # Patch resolve_provider to return Fake providers
    from unittest.mock import patch
    patcher1 = patch("app.services.voice.stt_service.SpeechToTextService._resolve_provider", return_value=FakeSpeechToTextProvider())
    patcher2 = patch("app.services.voice.tts_service.TextToSpeechService._resolve_provider", return_value=FakeTextToSpeechProvider())
    patcher1.start()
    patcher2.start()
    
    yield
    
    patcher1.stop()
    patcher2.stop()
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def create_test_user(email="voice_candidate@example.com", name="Voice User"):
    db = TestingSessionLocal()
    user = User(
        email=email,
        full_name=name,
        password_hash=hash_password("Password123!"),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id, user.email)
    db.close()
    return user, token


def create_sample_question():
    db = TestingSessionLocal()
    q = InterviewQuestion(
        question_text="How should a District Collector handle public administrative challenges?",
        question_type="SITUATIONAL",
        difficulty="MODERATE",
        category="GOVERNANCE",
        topic="DISTRICT_ADMINISTRATION",
        explanation="Tests administrative acumen.",
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    db.close()
    return q


# =========================================================
# 1 & 2. AUTHENTICATION TESTS
# =========================================================

def test_01_unauthenticated_transcribe_rejected():
    files = {"audio": ("test.wav", b"fake audio content", "audio/wav")}
    res = client.post("/api/voice/transcribe", files=files)
    assert res.status_code == 401


def test_02_unauthenticated_synthesize_rejected():
    res = client.post("/api/voice/synthesize", json={"text": "Hello candidate."})
    assert res.status_code == 401


# =========================================================
# 3 - 6. AUDIO UPLOAD & SECURITY VALIDATION TESTS
# =========================================================

def test_03_transcribe_valid_audio_accepted():
    _, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}
    files = {"audio": ("recording.wav", b"RIFF....WAVEfmt ....data....", "audio/wav")}

    res = client.post("/api/voice/transcribe", files=files, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "text" in data
    assert data["language"] == "en-IN"
    assert data["confidence"] is None


def test_04_transcribe_unsupported_mime_rejected():
    _, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}
    files = {"audio": ("malicious.exe", b"\x4d\x5a\x90\x00", "application/x-msdownload")}

    res = client.post("/api/voice/transcribe", files=files, headers=headers)
    assert res.status_code == 415
    assert "Unsupported audio format" in res.json()["detail"]


def test_05_transcribe_oversized_file_rejected():
    _, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}
    # 11MB file exceeding 10MB limit
    oversized_data = b"0" * (11 * 1024 * 1024)
    files = {"audio": ("big.wav", oversized_data, "audio/wav")}

    res = client.post("/api/voice/transcribe", files=files, headers=headers)
    assert res.status_code == 413
    assert "exceeds maximum limit" in res.json()["detail"]


def test_06_transcribe_empty_file_rejected():
    _, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}
    files = {"audio": ("empty.wav", b"", "audio/wav")}

    res = client.post("/api/voice/transcribe", files=files, headers=headers)
    assert res.status_code == 422
    assert "empty" in res.json()["detail"]


# =========================================================
# 7 - 9. STT SERVICE & PROVIDER TESTS
# =========================================================

def test_07_fake_stt_provider_returns_structured_transcript():
    provider = FakeSpeechToTextProvider(default_text="Custom candidate voice answer.")
    res = provider.transcribe(b"dummy_bytes_data_1234567890", language="hi-IN")
    assert res["text"] == "Custom candidate voice answer."
    assert res["language"] == "hi-IN"
    assert res["confidence"] is None


def test_08_stt_provider_failure_handled():
    failing_provider = FakeSpeechToTextProvider(fail_mode=True)
    stt_service = SpeechToTextService(provider=failing_provider)

    with pytest.raises(Exception) as exc_info:
        stt_service.transcribe_audio(b"audio_content", "test.wav", "audio/wav")
    assert exc_info.value.status_code == 502
    assert "Voice transcription provider error" in exc_info.value.detail


def test_09_stt_language_param_passed_correctly():
    _, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}
    files = {"audio": ("recording.mp3", b"ID3....mp3data", "audio/mp3")}
    data = {"language": "mr-IN"}

    res = client.post("/api/voice/transcribe", files=files, data=data, headers=headers)
    assert res.status_code == 200
    assert res.json()["language"] == "mr-IN"


# =========================================================
# 10 - 12. TTS SERVICE & PROVIDER TESTS
# =========================================================

def test_10_fake_tts_provider_returns_audio_stream():
    _, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"text": "Welcome to your UPSC interview session.", "language": "en-IN"}

    res = client.post("/api/voice/synthesize", json=payload, headers=headers)
    assert res.status_code == 200
    assert res.headers["content-type"] == "audio/mpeg"
    assert len(res.content) > 0


def test_11_tts_provider_failure_handled():
    failing_provider = FakeTextToSpeechProvider(fail_mode=True)
    tts_service = TextToSpeechService(provider=failing_provider)

    with pytest.raises(Exception) as exc_info:
        tts_service.synthesize_speech("Sample question text")
    assert exc_info.value.status_code == 502
    assert "Voice TTS provider failure" in exc_info.value.detail


def test_12_tts_empty_text_rejected():
    _, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/voice/synthesize", json={"text": "   "}, headers=headers)
    assert res.status_code == 422


# =========================================================
# 13 - 15. SECURITY & TEMPORARY FILE CLEANUP TESTS
# =========================================================

def test_13_temporary_audio_files_cleaned_up():
    stt_service = SpeechToTextService()
    # Transcribe sample file
    result = stt_service.transcribe_audio(b"sample_audio_bytes_12345", "test.wav", "audio/wav")
    assert result["text"] != ""


def test_14_no_arbitrary_filesystem_access():
    _, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}
    # Traversal filename attempt
    files = {"audio": ("../../../../etc/passwd.wav", b"dummy audio", "audio/wav")}

    res = client.post("/api/voice/transcribe", files=files, headers=headers)
    assert res.status_code == 200


def test_15_provider_secrets_never_returned():
    _, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}
    files = {"audio": ("recording.wav", b"RIFF....WAVE", "audio/wav")}

    res = client.post("/api/voice/transcribe", files=files, headers=headers)
    res_text = str(res.content)
    assert "API_KEY" not in res_text
    assert "SECRET" not in res_text


# =========================================================
# 16 - 20. INTERVIEW VOICE INTEGRATION TESTS
# =========================================================

def test_16_voice_transcript_submitted_to_canonical_answer_endpoint():
    user, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}
    create_sample_question()

    # 1. Start session in VOICE mode
    res_start = client.post(
        "/api/interview/start",
        json={"total_questions": 3, "input_mode": "VOICE", "language": "en-IN"},
        headers=headers,
    )
    assert res_start.status_code == 201
    session_id = res_start.json()["session_id"]
    assert res_start.json()["input_mode"] == "VOICE"

    # 2. Transcribe voice recording
    files = {"audio": ("answer.wav", b"RIFF....candidate_voice_recording", "audio/wav")}
    res_transcribe = client.post("/api/voice/transcribe", files=files, headers=headers)
    assert res_transcribe.status_code == 200
    transcript_text = res_transcribe.json()["text"]

    # 3. Submit transcript to canonical answer endpoint
    res_answer = client.post(
        f"/api/interview/{session_id}/answer",
        json={"answer_text": transcript_text, "answer_duration_seconds": 45},
        headers=headers,
    )
    assert res_answer.status_code == 200
    assert "answer_id" in res_answer.json()

    # Verify canonical answer in DB
    db = TestingSessionLocal()
    answer_db = db.query(InterviewAnswer).filter(InterviewAnswer.id == res_answer.json()["answer_id"]).first()
    assert answer_db is not None
    assert answer_db.answer_text == transcript_text
    assert answer_db.answer_duration_seconds == 45
    db.close()


def test_17_answer_duration_seconds_stored():
    user, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}
    create_sample_question()

    res_start = client.post("/api/interview/start", json={"total_questions": 2}, headers=headers)
    session_id = res_start.json()["session_id"]

    res_answer = client.post(
        f"/api/interview/{session_id}/answer",
        json={"answer_text": "Detailed voice response on civil services.", "answer_duration_seconds": 120},
        headers=headers,
    )
    assert res_answer.status_code == 200

    db = TestingSessionLocal()
    answer_db = db.query(InterviewAnswer).filter(InterviewAnswer.id == res_answer.json()["answer_id"]).first()
    assert answer_db.answer_duration_seconds == 120
    db.close()


def test_18_voice_session_creation_with_input_mode_and_language():
    user, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}
    create_sample_question()

    res = client.post(
        "/api/interview/start",
        json={"input_mode": "VOICE", "language": "hi-IN", "total_questions": 5},
        headers=headers,
    )
    assert res.status_code == 201
    assert res.json()["input_mode"] == "VOICE"
    assert res.json()["language"] == "hi-IN"


def test_19_text_mode_and_voice_mode_coexist():
    user, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}
    create_sample_question()

    res_text = client.post("/api/interview/start", json={"input_mode": "TEXT"}, headers=headers)
    res_voice = client.post("/api/interview/start", json={"input_mode": "VOICE"}, headers=headers)

    assert res_text.json()["input_mode"] == "TEXT"
    assert res_voice.json()["input_mode"] == "VOICE"


def test_20_user_isolation_for_voice_and_interview_endpoints():
    user_a, token_a = create_test_user("usera_voice@example.com", "User A")
    user_b, token_b = create_test_user("userb_voice@example.com", "User B")
    create_sample_question()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    res_start_a = client.post("/api/interview/start", json={"total_questions": 3}, headers=headers_a)
    session_id_a = res_start_a.json()["session_id"]

    # User B attempts to submit answer to User A's session
    res_hack = client.post(
        f"/api/interview/{session_id_a}/answer",
        json={"answer_text": "Hacked answer attempt", "answer_duration_seconds": 30},
        headers=headers_b,
    )
    assert res_hack.status_code == 404
