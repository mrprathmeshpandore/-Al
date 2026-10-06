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
from app.services.voice.providers.gemini_voice_provider import GeminiSpeechToTextProvider, GeminiTextToSpeechProvider
from app.services.question_generation_service import generate_interview_question
from app.services.answer_evaluation_service import AnswerEvaluationService
from app.services.interview_question_orchestrator import InterviewQuestionOrchestrator
from app.services.gemini_service import FakeGeminiService

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
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def create_test_user(email="multilingual_aspirant@example.com", name="Multilingual User"):
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
        question_text="How can civil servants ensure effective e-governance?",
        question_type="MAIN",
        difficulty="MODERATE",
        category="Public Administration",
        topic="Governance",
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    q_id = q.id
    db.close()
    return q_id


# ============================================================================
# 1. English, Marathi, Hindi Language Selection & Session Persistence
# ============================================================================
def test_1_english_language_selection_in_session():
    user, token = create_test_user("en_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    create_sample_question()

    res = client.post("/api/interview/start", json={"total_questions": 3, "language": "en-IN"}, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["session_id"] is not None

    db = TestingSessionLocal()
    session = db.query(InterviewSession).filter(InterviewSession.id == data["session_id"]).first()
    assert session.language == "en-IN"
    db.close()


def test_2_marathi_language_selection_in_session():
    user, token = create_test_user("mr_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    create_sample_question()

    res = client.post("/api/interview/start", json={"total_questions": 3, "language": "mr-IN"}, headers=headers)
    assert res.status_code == 201
    data = res.json()

    db = TestingSessionLocal()
    session = db.query(InterviewSession).filter(InterviewSession.id == data["session_id"]).first()
    assert session.language == "mr-IN"
    db.close()


def test_3_hindi_language_selection_in_session():
    user, token = create_test_user("hi_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    create_sample_question()

    res = client.post("/api/interview/start", json={"total_questions": 3, "language": "hi-IN"}, headers=headers)
    assert res.status_code == 201
    data = res.json()

    db = TestingSessionLocal()
    session = db.query(InterviewSession).filter(InterviewSession.id == data["session_id"]).first()
    assert session.language == "hi-IN"
    db.close()


# ============================================================================
# 4 & 5. STT and TTS Provider Multilingual Support
# ============================================================================
def test_4_stt_provider_multilingual():
    fake_stt = FakeSpeechToTextProvider()
    
    res_en = fake_stt.transcribe(b"dummy_audio", language="en-IN")
    assert res_en["language"] == "en-IN"
    assert len(res_en["text"]) > 0

    res_mr = fake_stt.transcribe(b"dummy_audio", language="mr-IN")
    assert res_mr["language"] == "mr-IN"
    assert "नुकसानीची" in res_mr["text"] or "लोकप्रशासन" in res_mr["text"] or "मराठी" in res_mr["text"]

    res_hi = fake_stt.transcribe(b"dummy_audio", language="hi-IN")
    assert res_hi["language"] == "hi-IN"
    assert "प्रशासन" in res_hi["text"] or "सिविल" in res_hi["text"] or "हिंदी" in res_hi["text"]


def test_5_tts_provider_multilingual():
    fake_tts = FakeTextToSpeechProvider()

    audio_en, mime_en = fake_tts.synthesize("Why do you want to join civil services?", language="en-IN")
    assert len(audio_en) > 0
    assert mime_en == "audio/mpeg"

    audio_mr, mime_mr = fake_tts.synthesize("तुम्हाला नागरी सेवेत का सहभागी व्हायचे आहे?", language="mr-IN")
    assert len(audio_mr) > 0

    audio_hi, mime_hi = fake_tts.synthesize("आप सिविल सेवा में क्यों शामिल होना चाहते हैं?", language="hi-IN")
    assert len(audio_hi) > 0


# ============================================================================
# 6 & 7. AI Question Generation & Adaptation in Target Language
# ============================================================================
def test_6_question_generation_language_context():
    db = TestingSessionLocal()
    fake_gemini = FakeGeminiService()
    user, _ = create_test_user("gen_lang_user@example.com")

    question_mr = generate_interview_question(
        topic="Governance",
        current_user_id=user.id,
        db=db,
        category="Polity",
        language="mr-IN",
        gemini_service=fake_gemini
    )
    assert question_mr is not None

    question_hi = generate_interview_question(
        topic="Administrative Reforms",
        current_user_id=user.id,
        db=db,
        category="Governance",
        language="hi-IN",
        gemini_service=fake_gemini
    )
    assert question_hi is not None
    db.close()


def test_7_orchestrator_question_adaptation_marathi():
    db = TestingSessionLocal()
    fake_gemini = FakeGeminiService()
    orchestrator = InterviewQuestionOrchestrator(db=db, gemini_service=fake_gemini)

    q = InterviewQuestion(
        question_text="What is your view on public administration?",
        question_type="MAIN",
        difficulty="MODERATE",
    )
    db.add(q)
    db.commit()

    adapted = orchestrator._adapt_question_language(q, "mr-IN")
    assert adapted is not None
    assert adapted.question_text is not None
    db.close()


# ============================================================================
# 8. Evaluation Language Support
# ============================================================================
def test_8_evaluation_language_feedback():
    db = TestingSessionLocal()
    user, _ = create_test_user("eval_user@example.com")
    user_obj = db.query(User).filter(User.id == user.id).first()

    session = InterviewSession(user_id=user.id, language="mr-IN", status=SessionStatus.IN_PROGRESS.value)
    db.add(session)
    db.flush()

    q = InterviewQuestion(question_text="तुम्ही नागरी सेवेत का येऊ इच्छिता?", question_type="MAIN")
    db.add(q)
    db.flush()

    sq = InterviewSessionQuestion(session_id=session.id, question_id=q.id, sequence_number=1)
    db.add(sq)
    db.flush()

    ans = InterviewAnswer(session_question_id=sq.id, answer_text="मला प्रशासनात पारदर्शकता आणि लोकसेवा सुधारायची आहे.")
    db.add(ans)
    db.commit()

    eval_service = AnswerEvaluationService(db=db, gemini_service=FakeGeminiService())
    evaluation = eval_service.evaluate_answer(answer_id=ans.id, user_id=user.id)
    assert evaluation is not None
    assert evaluation.overall_feedback is not None
    db.close()


# ============================================================================
# 9 & 10. STT & TTS Error Handling / Fallback Modes
# ============================================================================
def test_9_stt_failure_handling():
    user, token = create_test_user("stt_err@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Invalid audio size -> 413
    huge_audio = b"0" * (11 * 1024 * 1024)
    res_huge = client.post(
        "/api/voice/transcribe",
        files={"audio": ("large.wav", io.BytesIO(huge_audio), "audio/wav")},
        headers=headers,
    )
    assert res_huge.status_code == 413

    # Unsupported format -> 415
    res_fmt = client.post(
        "/api/voice/transcribe",
        files={"audio": ("test.xyz", io.BytesIO(b"data"), "application/octet-stream")},
        headers=headers,
    )
    assert res_fmt.status_code == 415


def test_10_tts_empty_text_rejection():
    user, token = create_test_user("tts_err@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post(
        "/api/voice/synthesize",
        json={"text": "   ", "language": "mr-IN"},
        headers=headers,
    )
    assert res.status_code == 422


# ============================================================================
# 11. Fake Provider Test Mode
# ============================================================================
def test_11_fake_provider_test_mode():
    stt_service = SpeechToTextService(provider=FakeSpeechToTextProvider())
    res = stt_service.transcribe_audio(b"RIFF....WAVE", "test.wav", "audio/wav", language="hi-IN")
    assert res["language"] == "hi-IN"
    assert "text" in res

    tts_service = TextToSpeechService(provider=FakeTextToSpeechProvider())
    audio, mime = tts_service.synthesize_speech("हिंदी परीक्षण", language="hi-IN")
    assert len(audio) > 0
    assert mime == "audio/mpeg"
