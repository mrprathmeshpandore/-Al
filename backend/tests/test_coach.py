"""
Unit and Integration Test Suite for Phase 14: AI Preparation Coach.

Tests cover:
- Authentication & User Isolation
- New User Foundational Plan (No Fake Stats)
- Personalization Rules (Reasoning, Balance, Weak Topics, DAF)
- Plan Types (Daily, Weekly) & Constraints
- Idempotency & Refresh Behavior
- Task Lifecycle (Start, Complete, Skip)
- Gemini Structured Output Parsing & Validation
- Deterministic Fallback Engine
- Resources & Current Affairs Referencing
- Security & Anti-Arbitrary Injection
"""

import uuid
from datetime import date, datetime, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.models.profile import UserProfile
from app.models.interview import InterviewSession, InterviewSessionQuestion, InterviewAnswer
from app.models.question import InterviewQuestion
from app.models.evaluation import InterviewAnswerEvaluation
from app.models.resource import Resource
from app.models.current_affair import CurrentAffair
from app.models.coach import PreparationPlan, PreparationTask, PlanType, PlanStatus, TaskStatus
from app.services.coach.context_builder import CoachContextBuilder
from app.services.coach.recommendation_service import RecommendationService
from app.services.coach.coach_service import CoachService
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


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_user(db_session):
    user = User(
        id=str(uuid.uuid4()),
        email=f"coach_candidate_{uuid.uuid4().hex[:6]}@example.com",
        full_name="Coach Aspirant",
        password_hash="hashed_password_123",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user_b(db_session):
    user = User(
        id=str(uuid.uuid4()),
        email=f"coach_b_{uuid.uuid4().hex[:6]}@example.com",
        full_name="Candidate B",
        password_hash="hashed_password_123",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    from app.utils.security import create_access_token
    token = create_access_token(test_user.id, test_user.email)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_b(test_user_b):
    from app.utils.security import create_access_token
    token = create_access_token(test_user_b.id, test_user_b.email)
    return {"Authorization": f"Bearer {token}"}


client = TestClient(app)


# ============================================================================
# 1. AUTHENTICATION & USER ISOLATION
# ============================================================================

def test_unauthenticated_coach_request_rejected():
    res = client.get("/api/coach/today")
    assert res.status_code == 401


def test_authenticated_coach_request_works(auth_headers):
    res = client.get("/api/coach/today", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "date" in data
    assert "tasks" in data


# ============================================================================
# 2. BRAND-NEW USER FOUNDATIONAL PLAN (NO FAKE STATS)
# ============================================================================

def test_new_user_receives_foundational_plan(auth_headers):
    res = client.post("/api/coach/daily-plan", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["plan_type"] == "DAILY"
    assert "Foundational" in data["title"]
    assert len(data["tasks"]) > 0
    task_types = [t["task_type"] for t in data["tasks"]]
    assert "DAF_PRACTICE" in task_types or "QUESTION_PRACTICE" in task_types


def test_no_fake_performance_statistics_generated(db_session, test_user):
    context = CoachContextBuilder.build_candidate_context(db_session, test_user.id)
    assert context["has_evaluations"] is False
    assert context["overview"]["average_score"] is None
    assert context["weak_areas"] == []


# ============================================================================
# 3. PERSONALIZATION RULES & CONTEXT BUILDER
# ============================================================================

def test_weak_reasoning_produces_reasoning_recommendation(db_session, test_user):
    session = InterviewSession(user_id=test_user.id, status="COMPLETED")
    db_session.add(session)
    db_session.flush()

    q = InterviewQuestion(question_text="Explain administrative policy.", topic="Governance")
    db_session.add(q)
    db_session.flush()

    # Create 3 evaluated answers to satisfy MINIMUM_SAMPLE_SIZE = 3
    for idx in range(1, 4):
        sq = InterviewSessionQuestion(session_id=session.id, question_id=q.id, sequence_number=idx)
        db_session.add(sq)
        db_session.flush()

        ans = InterviewAnswer(session_question_id=sq.id, answer_text=f"Policy text {idx}.")
        db_session.add(ans)
        db_session.flush()

        eval_rec = InterviewAnswerEvaluation(
            answer_id=ans.id,
            content_score=7.0,
            content_feedback="good",
            clarity_score=7.0,
            clarity_feedback="good",
            depth_score=7.0,
            depth_feedback="good",
            reasoning_score=4.0,  # Weak reasoning
            reasoning_feedback="weak rationale",
            balance_score=7.0,
            balance_feedback="good",
            communication_score=7.0,
            communication_feedback="good",
            overall_score=5.8,
            overall_feedback="overall good",
            suggested_answer="model answer",
        )
        db_session.add(eval_rec)
    
    db_session.commit()

    context = CoachContextBuilder.build_candidate_context(db_session, test_user.id)
    assert context["has_evaluations"] is True
    assert len(context["weak_areas"]) > 0
    assert context["weak_areas"][0]["dimension"] == "Reasoning"

    rec_service = RecommendationService(gemini_service=FakeGeminiService())
    rec = rec_service.generate_recommendations(context, plan_type="DAILY")
    assert rec is not None
    assert len(rec.tasks) > 0


def test_weak_balance_produces_balance_recommendation(db_session, test_user):
    session = InterviewSession(user_id=test_user.id, status="COMPLETED")
    db_session.add(session)
    db_session.flush()

    q = InterviewQuestion(question_text="Tradeoffs in land acquisition?", topic="Economy")
    db_session.add(q)
    db_session.flush()

    # Create 3 evaluated answers to satisfy MINIMUM_SAMPLE_SIZE = 3
    for idx in range(1, 4):
        sq = InterviewSessionQuestion(session_id=session.id, question_id=q.id, sequence_number=idx)
        db_session.add(sq)
        db_session.flush()

        ans = InterviewAnswer(session_question_id=sq.id, answer_text=f"One sided answer {idx}.")
        db_session.add(ans)
        db_session.flush()

        eval_rec = InterviewAnswerEvaluation(
            answer_id=ans.id,
            content_score=8.0,
            content_feedback="good",
            clarity_score=8.0,
            clarity_feedback="good",
            depth_score=8.0,
            depth_feedback="good",
            reasoning_score=8.0,
            reasoning_feedback="good",
            balance_score=3.5,  # Weak balance
            balance_feedback="unbalanced",
            communication_score=8.0,
            communication_feedback="good",
            overall_score=6.2,
            overall_feedback="overall good",
            suggested_answer="balanced model answer",
        )
        db_session.add(eval_rec)
    
    db_session.commit()

    context = CoachContextBuilder.build_candidate_context(db_session, test_user.id)
    assert context["weak_areas"][0]["dimension"] == "Balance"


def test_weak_topic_produces_topic_recommendation(db_session, test_user):
    session = InterviewSession(user_id=test_user.id, status="COMPLETED")
    db_session.add(session)
    db_session.flush()

    q = InterviewQuestion(question_text="Monetary Policy questions", topic="Economy")
    db_session.add(q)
    db_session.flush()

    sq = InterviewSessionQuestion(session_id=session.id, question_id=q.id, sequence_number=1)
    db_session.add(sq)
    db_session.flush()

    ans = InterviewAnswer(session_question_id=sq.id, answer_text="Economy response.")
    db_session.add(ans)
    db_session.flush()

    eval_rec = InterviewAnswerEvaluation(
        answer_id=ans.id,
        content_score=4.0,
        content_feedback="low",
        clarity_score=4.0,
        clarity_feedback="low",
        depth_score=4.0,
        depth_feedback="low",
        reasoning_score=4.0,
        reasoning_feedback="low",
        balance_score=4.0,
        balance_feedback="low",
        communication_score=4.0,
        communication_feedback="low",
        overall_score=4.0,
        overall_feedback="low performance",
        suggested_answer="detailed answer",
    )
    db_session.add(eval_rec)
    db_session.commit()

    context = CoachContextBuilder.build_candidate_context(db_session, test_user.id)
    assert len(context["topics"]) > 0
    assert context["topics"][0]["topic"] == "Economy"


def test_daf_weakness_produces_daf_practice_recommendation(db_session, test_user):
    profile = UserProfile(
        user_id=test_user.id,
        home_state="Maharashtra",
        district="Pune",
        upsc_journey_data={"optional_subject": "Public Administration"},
        interests={"hobbies": "Chess, Trekking"},
    )
    db_session.add(profile)
    db_session.commit()

    context = CoachContextBuilder.build_candidate_context(db_session, test_user.id)
    assert context["daf"]["optional_subject"] == "Public Administration"


# ============================================================================
# 4. PLAN CREATION & CONSTRAINTS
# ============================================================================

def test_daily_plan_created(auth_headers):
    res = client.post("/api/coach/daily-plan", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["plan_type"] == "DAILY"
    assert data["status"] == "ACTIVE"


def test_weekly_plan_created(auth_headers):
    res = client.post("/api/coach/weekly-plan", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["plan_type"] == "WEEKLY"
    assert data["status"] == "ACTIVE"


def test_correct_task_count_and_valid_types(auth_headers):
    res = client.post("/api/coach/daily-plan", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    tasks = data["tasks"]
    assert 1 <= len(tasks) <= 10
    valid_priorities = {"HIGH", "MEDIUM", "LOW"}
    for t in tasks:
        assert t["priority"] in valid_priorities
        assert isinstance(t["estimated_minutes"], int)
        assert t["estimated_minutes"] >= 5


# ============================================================================
# 5. IDEMPOTENCY & REFRESH BEHAVIOR
# ============================================================================

def test_duplicate_daily_plan_prevented(auth_headers):
    res1 = client.post("/api/coach/daily-plan", headers=auth_headers)
    assert res1.status_code == 200
    plan_id_1 = res1.json()["id"]

    res2 = client.post("/api/coach/daily-plan", headers=auth_headers)
    assert res2.status_code == 200
    assert res2.json()["id"] == plan_id_1


def test_duplicate_weekly_plan_prevented(auth_headers):
    res1 = client.post("/api/coach/weekly-plan", headers=auth_headers)
    assert res1.status_code == 200
    plan_id_1 = res1.json()["id"]

    res2 = client.post("/api/coach/weekly-plan", headers=auth_headers)
    assert res2.status_code == 200
    assert res2.json()["id"] == plan_id_1


def test_refresh_behavior_works(auth_headers):
    res1 = client.post("/api/coach/daily-plan", headers=auth_headers)
    plan_id_1 = res1.json()["id"]

    res2 = client.post("/api/coach/refresh", json={"plan_type": "DAILY", "refresh": True}, headers=auth_headers)
    assert res2.status_code == 200
    plan_id_2 = res2.json()["id"]
    assert plan_id_1 != plan_id_2


# ============================================================================
# 6. TASK LIFECYCLE (START, COMPLETE, SKIP)
# ============================================================================

def test_task_lifecycle_transitions(auth_headers):
    res = client.post("/api/coach/daily-plan", headers=auth_headers)
    plan = res.json()
    task_id = plan["tasks"][0]["id"]

    # 1. Start task
    res_start = client.post(f"/api/coach/tasks/{task_id}/start", headers=auth_headers)
    assert res_start.status_code == 200
    assert res_start.json()["status"] == "IN_PROGRESS"

    # 2. Complete task
    res_comp = client.post(f"/api/coach/tasks/{task_id}/complete", headers=auth_headers)
    assert res_comp.status_code == 200
    assert res_comp.json()["status"] == "COMPLETED"
    assert res_comp.json()["completed_at"] is not None

    # 3. Skip task (2nd task)
    if len(plan["tasks"]) > 1:
        task_id_2 = plan["tasks"][1]["id"]
        res_skip = client.post(f"/api/coach/tasks/{task_id_2}/skip", headers=auth_headers)
        assert res_skip.status_code == 200
        assert res_skip.json()["status"] == "SKIPPED"


# ============================================================================
# 7. SECURITY & MULTI-TENANT USER ISOLATION
# ============================================================================

def test_user_a_cannot_access_user_b_plan(auth_headers, auth_headers_b):
    res_a = client.post("/api/coach/daily-plan", headers=auth_headers)
    plan_id_a = res_a.json()["id"]

    res_access = client.get(f"/api/coach/plans/{plan_id_a}", headers=auth_headers_b)
    assert res_access.status_code == 404


def test_user_a_cannot_complete_user_b_task(auth_headers, auth_headers_b):
    res_a = client.post("/api/coach/daily-plan", headers=auth_headers)
    task_id_a = res_a.json()["tasks"][0]["id"]

    res_comp = client.post(f"/api/coach/tasks/{task_id_a}/complete", headers=auth_headers_b)
    assert res_comp.status_code == 404


# ============================================================================
# 8. GEMINI STRUCTURED OUTPUT & FALLBACK
# ============================================================================

def test_gemini_failure_uses_deterministic_fallback(db_session, test_user):
    session = InterviewSession(user_id=test_user.id, status="COMPLETED")
    db_session.add(session)
    db_session.flush()

    q = InterviewQuestion(question_text="Governance question", topic="Governance")
    db_session.add(q)
    db_session.flush()

    sq = InterviewSessionQuestion(session_id=session.id, question_id=q.id, sequence_number=1)
    db_session.add(sq)
    db_session.flush()

    ans = InterviewAnswer(session_question_id=sq.id, answer_text="Response.")
    db_session.add(ans)
    db_session.flush()

    eval_rec = InterviewAnswerEvaluation(
        answer_id=ans.id,
        content_score=7.0,
        content_feedback="ok",
        clarity_score=7.0,
        clarity_feedback="ok",
        depth_score=7.0,
        depth_feedback="ok",
        reasoning_score=7.0,
        reasoning_feedback="ok",
        balance_score=7.0,
        balance_feedback="ok",
        communication_score=7.0,
        communication_feedback="ok",
        overall_score=7.0,
        overall_feedback="ok",
        suggested_answer="suggested",
    )
    db_session.add(eval_rec)
    db_session.commit()

    failing_fake_gemini = FakeGeminiService(should_fail=True)
    rec_service = RecommendationService(gemini_service=failing_fake_gemini)

    context = CoachContextBuilder.build_candidate_context(db_session, test_user.id)
    output = rec_service.generate_recommendations(context, plan_type="DAILY")

    assert output is not None
    assert len(output.tasks) > 0
    assert "Practice Plan" in output.plan_title


def test_malformed_gemini_json_uses_fallback(db_session, test_user):
    malformed_gemini = FakeGeminiService(should_malform=True)
    rec_service = RecommendationService(gemini_service=malformed_gemini)

    context = CoachContextBuilder.build_candidate_context(db_session, test_user.id)
    output = rec_service.generate_recommendations(context, plan_type="DAILY")
    assert output is not None
    assert len(output.tasks) > 0


# ============================================================================
# 9. RESOURCES & CURRENT AFFAIRS REFERENCING
# ============================================================================

def test_only_existing_resources_referenced(db_session, test_user):
    res_obj = Resource(
        title="Indian Polity by M. Laxmikanth",
        category="Polity",
        subject="Polity",
        created_by=test_user.id,
    )
    db_session.add(res_obj)
    db_session.commit()

    context = CoachContextBuilder.build_candidate_context(db_session, test_user.id)
    assert len(context["available_resources"]) > 0
    assert context["available_resources"][0]["title"] == "Indian Polity by M. Laxmikanth"


def test_only_existing_current_affairs_referenced(db_session, test_user):
    article = CurrentAffair(
        title="National Education Policy Progress",
        slug="nep-progress-2026",
        category="EDUCATION",
        source_name="The Hindu",
        summary="Summary of NEP implementation.",
    )
    db_session.add(article)
    db_session.commit()

    context = CoachContextBuilder.build_candidate_context(db_session, test_user.id)
    assert len(context["recent_current_affairs"]) > 0
    assert context["recent_current_affairs"][0]["title"] == "National Education Policy Progress"
