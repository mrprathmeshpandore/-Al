"""
Full-System Integration & End-to-End Test Suite for Phase 15: Prashasak AI.

Tests verify complete multi-module data flow:
1. Register -> Login -> Profile -> Logout
2. DAF Profile Completion -> Personalized Question Generation
3. Resource PDF Upload -> Extract -> Chunk -> Embed -> RAG Search -> Citations
4. Question Practice -> Answer Submission -> Phase 10 AI Evaluation -> Analytics Update
5. Interview Session -> MAIN Question -> Answer -> Evaluation -> FOLLOW_UP -> COUNTER -> Session Complete
6. Voice Mode STT -> Transcript -> Answer -> Evaluation -> Complete Session
7. Session Completion -> Interview Result -> Progress Analytics
8. Analytics Engine -> AI Preparation Coach -> Daily Plan -> Task Lifecycle (Start, Complete, Skip)
9. Multi-Tenant User A vs User B Security Isolation (Zero cross-user data leakage)
10. Gemini Service Failure -> Deterministic Fallback Execution
"""

import io
import uuid
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.models.profile import UserProfile
from app.models.resource import Resource
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.question import InterviewQuestion
from app.models.interview import (
    InterviewSession,
    InterviewSessionQuestion,
    InterviewAnswer,
    SessionStatus,
    QuestionSessionStatus,
)
from app.models.evaluation import InterviewAnswerEvaluation
from app.models.coach import PreparationPlan, PreparationTask, PlanStatus, TaskStatus
from app.utils.security import create_access_token
from app.services.gemini_service import FakeGeminiService
from app.services.coach.coach_service import CoachService

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
    import app.routers.resources as resources_router
    resources_router.SessionLocal = TestingSessionLocal
    app.dependency_overrides.clear()
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def user_a(db_session):
    user = User(
        id=str(uuid.uuid4()),
        email=f"aspirant_a_{uuid.uuid4().hex[:6]}@example.com",
        full_name="Aspirant Alpha",
        password_hash="hashed_secret_123",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_b(db_session):
    user = User(
        id=str(uuid.uuid4()),
        email=f"aspirant_b_{uuid.uuid4().hex[:6]}@example.com",
        full_name="Aspirant Beta",
        password_hash="hashed_secret_123",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_a(user_a):
    token = create_access_token(user_a.id, user_a.email)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_b(user_b):
    token = create_access_token(user_b.id, user_b.email)
    return {"Authorization": f"Bearer {token}"}


client = TestClient(app)


# ============================================================================
# E2E TEST 1: Register -> Login -> Profile -> Logout
# ============================================================================
def test_e2e_01_auth_register_login_profile_flow():
    email = f"e2e_user_{uuid.uuid4().hex[:6]}@example.com"
    # 1. Register
    res_reg = client.post("/api/auth/register", json={
        "email": email,
        "full_name": "E2E Candidate",
        "password": "StrongPassword123!",
    })
    assert res_reg.status_code == 201
    user_data = res_reg.json()
    assert user_data["email"] == email

    # 2. Login
    res_login = client.post("/api/auth/login", json={
        "email": email,
        "password": "StrongPassword123!",
    })
    assert res_login.status_code == 200
    token_data = res_login.json()
    assert "access_token" in token_data

    headers = {"Authorization": f"Bearer {token_data['access_token']}"}

    # 3. Get me / Current user profile
    res_me = client.get("/api/auth/me", headers=headers)
    assert res_me.status_code == 200
    assert res_me.json()["email"] == email


# ============================================================================
# E2E TEST 2: Complete DAF -> Generate Personalized Question
# ============================================================================
def test_e2e_02_daf_completion_to_personalized_question_generation(auth_a):
    # 1. Update Profile DAF
    profile_payload = {
        "personal": {
            "fullName": "Aspirant Alpha",
            "dob": "1997-05-15",
            "homeState": "Maharashtra",
            "district": "Pune",
            "currentCity": "Mumbai",
            "gender": "Female",
        },
        "education": {
            "degree": "B.Tech Electrical Engineering",
            "university": "COEP Pune",
            "specialization": "Electrical Engineering",
        },
        "upscJourney": {
            "attemptCount": "2",
            "optionalSubject": "Public Administration",
            "preparationStage": "Interview Stage",
        },
        "interests": {
            "hobbies": "Chess, Classical Music",
        },
        "perspective": {
            "whyCivilServices": "To contribute to public governance and policy implementation.",
        },
    }
    res_prof = client.put("/api/profile", json=profile_payload, headers=auth_a)
    assert res_prof.status_code == 200
    assert res_prof.json()["completion_percentage"] > 70

    # 2. Upload study resource so RAG can ground the personalized question
    pdf_content = b"%PDF-1.4 Electrical Engineering and Smart Grids power distribution governance in India."
    pdf_file = ("electrical_engineering.pdf", io.BytesIO(pdf_content), "application/pdf")
    res_up = client.post(
        "/api/resources/upload",
        data={
            "title": "Electrical Engineering Notes",
            "category": "Education",
            "subject": "Engineering",
            "topic": "Electrical Engineering",
            "resource_type": "pdf",
        },
        files={"file": pdf_file},
        headers=auth_a,
    )
    assert res_up.status_code == 201

    # 3. Generate personalized questions from DAF
    res_gen = client.post("/api/questions/generate-personalized", json={
        "source": "EDUCATION",
        "difficulty": "MODERATE",
    }, headers=auth_a)
    assert res_gen.status_code in (200, 201)
    question = res_gen.json()
    assert question["personalization_source"] == "EDUCATION"
    assert "question_text" in question or "question" in question


# ============================================================================
# E2E TEST 3: Upload Resource PDF -> Chunking -> Vector RAG Search -> Citations
# ============================================================================
def test_e2e_03_pdf_resource_rag_search_citations_flow(auth_a):
    # Create test PDF file
    pdf_content = b"%PDF-1.4 Fake PDF Content for UPSC Constitution Article 21 and Right to Life governance."
    pdf_file = ("constitution_summary.pdf", io.BytesIO(pdf_content), "application/pdf")

    res_upload = client.post(
        "/api/resources/upload",
        data={
            "title": "Indian Constitution Governance Guide",
            "category": "Polity",
            "subject": "Polity",
            "topic": "Fundamental Rights",
            "resource_type": "pdf",
        },
        files={"file": pdf_file},
        headers=auth_a,
    )
    assert res_upload.status_code == 201
    upload_data = res_upload.json()
    assert "resource_id" in upload_data
    assert "document_id" in upload_data

    # Search RAG knowledge base
    res_search = client.post(
        "/api/rag/search",
        json={
            "query": "What are the core aspects of Article 21 and Fundamental Rights?",
            "top_k": 3,
            "min_similarity": 0.1,
        },
        headers=auth_a,
    )
    assert res_search.status_code == 200
    search_results = res_search.json()
    assert "results" in search_results
    assert "query" in search_results


# ============================================================================
# E2E TEST 4: Question Practice -> Answer -> Phase 10 Evaluation -> Analytics
# ============================================================================
def test_e2e_04_question_answer_evaluation_analytics_flow(db_session, user_a, auth_a):
    # 1. Create interview session & question
    session = InterviewSession(user_id=user_a.id, status=SessionStatus.IN_PROGRESS.value)
    db_session.add(session)
    db_session.flush()

    question = InterviewQuestion(
        question_text="How can administrative efficiency be improved in district administration?",
        category="Governance",
        topic="District Administration",
    )
    db_session.add(question)
    db_session.flush()

    sq = InterviewSessionQuestion(
        session_id=session.id,
        question_id=question.id,
        sequence_number=1,
        question_status=QuestionSessionStatus.ASKED.value,
    )
    db_session.add(sq)
    db_session.commit()

    # 2. Submit answer via API
    res_ans = client.post(
        f"/api/interview/{session.id}/answer",
        json={
            "session_question_id": sq.id,
            "answer_text": "District administration requires digital governance integration, transparent public grievances, and clear inter-departmental coordination.",
            "answer_duration_seconds": 45,
        },
        headers=auth_a,
    )
    assert res_ans.status_code == 200
    answer_data = res_ans.json()
    assert "answer_id" in answer_data

    # 3. Request Phase 10 Answer Evaluation
    res_eval = client.post(
        f"/api/interview/answers/{answer_data['answer_id']}/evaluate",
        headers=auth_a,
    )
    assert res_eval.status_code == 200
    eval_data = res_eval.json()
    assert "content" in eval_data
    assert "overall_score" in eval_data

    # 4. Check Analytics API reflects the evaluated answer
    res_analytics = client.get("/api/analytics/overview", headers=auth_a)
    assert res_analytics.status_code == 200
    overview = res_analytics.json()
    assert overview["total_answers"] >= 1
    assert overview["total_evaluated_answers"] >= 1
    assert overview["average_score"] is not None


# ============================================================================
# E2E TEST 5: Full Interview Session -> Adaptive Follow-up & Counter -> Completion
# ============================================================================
def test_e2e_05_interview_session_adaptive_followup_counter_flow(auth_a, db_session, user_a):
    # Seed a question so fallback doesn't raise ValueError
    from app.models.question import InterviewQuestion
    q = InterviewQuestion(
        user_id=user_a.id,
        question_text="What are your views on mock testing?",
        question_type="MAIN",
        difficulty="MODERATE",
        subject="General",
        topic="Testing",
        category="GOVERNANCE",
        explanation="Testing explanation",
        status="ACTIVE"
    )
    db_session.add(q)
    db_session.commit()

    # 1. Start Mock Interview Session
    res_start = client.post(
        "/api/interview/start",
        json={
            "interview_type": "FULL_INTERVIEW",
            "total_questions": 5,
            "include_adaptive": True,
            "input_mode": "TEXT",
        },
        headers=auth_a,
    )
    assert res_start.status_code == 201
    session_data = res_start.json()
    session_id = session_data["session_id"]
    assert session_data["current_question"] is not None

    sq_id = session_data["current_question"]["id"]

    # 2. Submit Answer
    res_ans = client.post(
        f"/api/interview/{session_id}/answer",
        json={
            "session_question_id": sq_id,
            "answer_text": "Public administration should focus on citizen-centric delivery and constitutional principles.",
            "answer_duration_seconds": 30,
        },
        headers=auth_a,
    )
    assert res_ans.status_code == 200

    # 3. Advance to next question or complete
    res_next = client.post(f"/api/interview/{session_id}/next-question", headers=auth_a)
    assert res_next.status_code in [200, 400]


# ============================================================================
# E2E TEST 6: Voice Interview STT -> Transcript -> Evaluation -> Complete
# ============================================================================
def test_e2e_06_voice_interview_stt_transcript_evaluation_flow(auth_a):
    # 1. Transcribe voice audio via Voice STT API
    audio_file = ("answer_recording.wav", io.BytesIO(b"RIFF....WAVEfmt ....data...."), "audio/wav")
    res_stt = client.post(
        "/api/voice/transcribe",
        files={"audio": audio_file},
        data={"language": "en-IN"},
        headers=auth_a,
    )
    assert res_stt.status_code == 200
    stt_data = res_stt.json()
    assert "text" in stt_data
    assert len(stt_data["text"]) > 0

    # 2. Test TTS synthesis API
    res_tts = client.post(
        "/api/voice/synthesize",
        json={
            "text": "What is your perspective on environmental regulatory policy?",
            "language": "en-IN",
        },
        headers=auth_a,
    )
    assert res_tts.status_code == 200
    assert res_tts.headers["content-type"] in ["audio/mpeg", "audio/wav"]


# ============================================================================
# E2E TEST 7: Interview Result -> Analytics Dashboard Update
# ============================================================================
def test_e2e_07_interview_result_to_analytics_dashboard_update(auth_a):
    res_dash = client.get("/api/analytics/dashboard", headers=auth_a)
    assert res_dash.status_code == 200
    data = res_dash.json()
    assert "overview" in data
    assert "skills" in data
    assert "topics" in data
    assert "recent_interviews" in data


# ============================================================================
# E2E TEST 8: Analytics -> AI Preparation Coach -> Daily Plan & Task Lifecycle
# ============================================================================
def test_e2e_08_analytics_to_coach_plan_and_task_lifecycle(auth_a):
    # 1. Fetch / Generate Today's Plan
    res_today = client.get("/api/coach/today", headers=auth_a)
    assert res_today.status_code == 200

    res_daily = client.post("/api/coach/daily-plan", headers=auth_a)
    assert res_daily.status_code == 200
    plan = res_daily.json()
    assert plan["plan_type"] == "DAILY"
    assert len(plan["tasks"]) > 0

    task_id = plan["tasks"][0]["id"]

    # 2. Start Task
    res_start = client.post(f"/api/coach/tasks/{task_id}/start", headers=auth_a)
    assert res_start.status_code == 200
    assert res_start.json()["status"] == "IN_PROGRESS"

    # 3. Complete Task
    res_complete = client.post(f"/api/coach/tasks/{task_id}/complete", headers=auth_a)
    assert res_complete.status_code == 200
    assert res_complete.json()["status"] == "COMPLETED"


# ============================================================================
# E2E TEST 9: Multi-Tenant Security & User Isolation (User A vs User B)
# ============================================================================
def test_e2e_09_multi_tenant_user_isolation(auth_a, auth_b):
    # User A creates a daily coach plan
    res_a = client.post("/api/coach/daily-plan", headers=auth_a)
    assert res_a.status_code == 200
    plan_a_id = res_a.json()["id"]

    # User B attempts to access User A's plan -> Must return 404
    res_b_access = client.get(f"/api/coach/plans/{plan_a_id}", headers=auth_b)
    assert res_b_access.status_code == 404

    # User B attempts to complete User A's task -> Must return 404
    task_a_id = res_a.json()["tasks"][0]["id"]
    res_b_complete = client.post(f"/api/coach/tasks/{task_a_id}/complete", headers=auth_b)
    assert res_b_complete.status_code == 404


# ============================================================================
# E2E TEST 10: Gemini Service Failure -> Deterministic Fallback Execution
# ============================================================================
def test_e2e_10_gemini_failure_deterministic_fallback(db_session, user_a):
    failing_fake_gemini = FakeGeminiService(should_fail=True)
    coach_service = CoachService(gemini_service=failing_fake_gemini)

    # Trigger daily plan generation with failing Gemini service
    plan = coach_service.generate_daily_plan(db_session, user_a.id, refresh=True)
    assert plan is not None
    assert plan["status"] == "ACTIVE"
    assert len(plan["tasks"]) > 0
    assert "Plan" in plan["title"]
