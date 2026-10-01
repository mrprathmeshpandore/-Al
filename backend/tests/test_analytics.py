import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.models.question import InterviewQuestion
from app.models.interview import InterviewSession, InterviewSessionQuestion, InterviewAnswer, SessionStatus, QuestionSessionStatus
from app.models.evaluation import InterviewAnswerEvaluation
from app.utils.security import hash_password, create_access_token

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


def create_test_user(email="analytics_candidate@example.com", name="Analytics Candidate"):
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


def create_sample_question(topic="Polity & Constitution", category="GS Paper II"):
    db = TestingSessionLocal()
    q = InterviewQuestion(
        question_text="Examine the federal balance under Article 356.",
        question_type="MAIN",
        difficulty="MODERATE",
        category=category,
        topic=topic,
        explanation="Constitutional governance test.",
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    db.close()
    return q


def seed_user_interview_with_evaluations(user, num_evals=3, overall_scores=None, input_mode="TEXT"):
    db = TestingSessionLocal()
    q = create_sample_question()
    now = datetime.now(timezone.utc)

    session = InterviewSession(
        user_id=user.id,
        status=SessionStatus.COMPLETED.value,
        interview_type="FULL_INTERVIEW",
        total_questions=num_evals,
        current_question_index=num_evals,
        input_mode=input_mode,
        language="en-IN",
        started_at=now - timedelta(hours=1),
        completed_at=now,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    session_id = session.id

    scores = overall_scores or [7.5, 8.0, 6.5]
    for idx, score in enumerate(scores[:num_evals]):
        sq = InterviewSessionQuestion(
            session_id=session_id,
            question_id=q.id,
            sequence_number=idx + 1,
            question_status=QuestionSessionStatus.ANSWERED.value,
            question_depth=0,
            adaptive_type="MAIN",
            presented_at=now - timedelta(minutes=30 - idx * 5),
        )
        db.add(sq)
        db.commit()
        db.refresh(sq)

        ans = InterviewAnswer(
            session_question_id=sq.id,
            answer_text=f"Candidate detailed answer text number {idx + 1}.",
            answer_duration_seconds=45,
            submitted_at=now - timedelta(minutes=25 - idx * 5),
        )
        db.add(ans)
        db.commit()
        db.refresh(ans)

        eval_rec = InterviewAnswerEvaluation(
            answer_id=ans.id,
            overall_score=score,
            content_score=score,
            clarity_score=score,
            depth_score=score,
            reasoning_score=score,
            balance_score=score,
            communication_score=score,
            overall_feedback="Good governance reasoning.",
            content_feedback="Accurate constitutional facts.",
            clarity_feedback="Clear points.",
            depth_feedback="Adequate depth.",
            reasoning_feedback="Sound logic.",
            balance_feedback="Balanced perspective.",
            communication_feedback="Good tone.",
            strengths=["Factual grounding", "Clear structure"],
            areas_to_improve=["Cite landmark cases"],
            suggested_answer="Model answer text.",
        )
        db.add(eval_rec)
        db.commit()

    db.close()
    return session_id


# =========================================================
# 1 & 2. AUTHENTICATION TESTS
# =========================================================

def test_01_authenticated_overview_works():
    user, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/analytics/overview", headers=headers)
    assert res.status_code == 200
    assert "total_questions_practiced" in res.json()


def test_02_unauthenticated_analytics_rejected():
    res = client.get("/api/analytics/overview")
    assert res.status_code == 401


# =========================================================
# 3 - 8. OVERVIEW METRICS & SCORE CALCULATION TESTS
# =========================================================

def test_03_to_07_overview_counts_and_average_calculation():
    user, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Seed session with 3 evaluations (7.0, 8.0, 9.0 -> Avg 8.0)
    seed_user_interview_with_evaluations(user, num_evals=3, overall_scores=[7.0, 8.0, 9.0])

    res = client.get("/api/analytics/overview", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["total_questions_practiced"] == 3
    assert data["total_interviews_started"] == 1
    assert data["total_interviews_completed"] == 1
    assert data["total_answers"] == 3
    assert data["total_evaluated_answers"] == 3
    assert data["average_score"] == 8.0
    assert data["highest_score"] == 9.0
    assert data["lowest_score"] == 7.0


def test_08_no_evaluations_returns_null_average():
    user, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/analytics/overview", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["total_questions_practiced"] == 0
    assert data["average_score"] is None
    assert data["highest_score"] is None
    assert data["lowest_score"] is None


# =========================================================
# 9 - 14. SKILL ANALYSIS TESTS
# =========================================================

def test_09_to_14_skill_breakdown_scores():
    user, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}

    seed_user_interview_with_evaluations(user, num_evals=2, overall_scores=[6.0, 8.0])

    res = client.get("/api/analytics/skills", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["content"]["average_score"] == 7.0
    assert data["clarity"]["average_score"] == 7.0
    assert data["depth"]["average_score"] == 7.0
    assert data["reasoning"]["average_score"] == 7.0
    assert data["balance"]["average_score"] == 7.0
    assert data["communication"]["average_score"] == 7.0


# =========================================================
# 15 - 17. TRENDS & PERIOD FILTER TESTS
# =========================================================

def test_15_to_17_score_trends_and_periods():
    user, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}

    seed_user_interview_with_evaluations(user, num_evals=2, overall_scores=[7.0, 8.0])

    res = client.get("/api/analytics/trends?period=30d", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["period"] == "30d"
    assert len(data["points"]) > 0
    assert "average_score" in data["points"][0]


# =========================================================
# 18 & 19. TOPIC PERFORMANCE TESTS
# =========================================================

def test_18_and_19_topic_performance_aggregation():
    user, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}

    seed_user_interview_with_evaluations(user, num_evals=2, overall_scores=[8.0, 8.6])

    res = client.get("/api/analytics/topics", headers=headers)
    assert res.status_code == 200
    topics = res.json()

    assert len(topics) > 0
    assert topics[0]["topic"] == "GS Paper II"
    assert topics[0]["average_score"] == 8.3
    assert topics[0]["evaluated_answers"] == 2


# =========================================================
# 20 - 23. INTERVIEW HISTORY ANALYTICS TESTS
# =========================================================

def test_20_to_23_interview_history_pagination_and_isolation():
    user_a, token_a = create_test_user("user_hist_a@example.com", "User History A")
    user_b, token_b = create_test_user("user_hist_b@example.com", "User History B")

    seed_user_interview_with_evaluations(user_a, num_evals=2)
    seed_user_interview_with_evaluations(user_b, num_evals=1)

    headers_a = {"Authorization": f"Bearer {token_a}"}
    res_a = client.get("/api/analytics/history?page=1&page_size=10", headers=headers_a)
    assert res_a.status_code == 200
    data_a = res_a.json()

    assert data_a["total"] == 1
    assert data_a["items"][0]["evaluated_answers"] == 2

    # Verify user B gets only User B history
    headers_b = {"Authorization": f"Bearer {token_b}"}
    res_b = client.get("/api/analytics/history", headers=headers_b)
    assert res_b.status_code == 200
    data_b = res_b.json()
    assert data_b["total"] == 1
    assert data_b["items"][0]["evaluated_answers"] == 1


# =========================================================
# 24 - 27. ADAPTIVE ANALYTICS TESTS
# =========================================================

def test_24_to_27_adaptive_question_statistics():
    user, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}

    db = TestingSessionLocal()
    q = create_sample_question()
    session = InterviewSession(user_id=user.id, status="IN_PROGRESS", total_questions=3)
    db.add(session)
    db.commit()
    db.refresh(session)

    # 1 MAIN, 1 FOLLOW_UP, 1 COUNTER
    sq1 = InterviewSessionQuestion(session_id=session.id, question_id=q.id, sequence_number=1, question_depth=0, adaptive_type="MAIN")
    sq2 = InterviewSessionQuestion(session_id=session.id, question_id=q.id, sequence_number=2, question_depth=1, adaptive_type="FOLLOW_UP")
    sq3 = InterviewSessionQuestion(session_id=session.id, question_id=q.id, sequence_number=3, question_depth=2, adaptive_type="COUNTER")
    db.add_all([sq1, sq2, sq3])
    db.commit()
    db.close()

    res = client.get("/api/analytics/adaptive", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["main_questions"] == 1
    assert data["follow_up_questions"] == 1
    assert data["counter_questions"] == 1
    assert data["follow_up_trigger_rate"] == 100.0
    assert data["counter_trigger_rate"] == 100.0


# =========================================================
# 28 - 30. WEAK & STRONG AREA THRESHOLD TESTS
# =========================================================

def test_28_to_30_weak_and_strong_area_thresholds():
    user, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Seed 3 evaluations with low score 5.0 (Weak area threshold < 6.0)
    seed_user_interview_with_evaluations(user, num_evals=3, overall_scores=[5.0, 5.0, 5.0])

    res_weak = client.get("/api/analytics/weak-areas", headers=headers)
    assert res_weak.status_code == 200
    weak_data = res_weak.json()

    assert len(weak_data) > 0
    assert weak_data[0]["average_score"] == 5.0
    assert weak_data[0]["sample_size"] == 3
    assert "improvement_needed" in weak_data[0]

    # Seed high scores for strong areas (Threshold >= 7.5)
    user2, token2 = create_test_user("strong_user@example.com", "Strong User")
    headers2 = {"Authorization": f"Bearer {token2}"}
    seed_user_interview_with_evaluations(user2, num_evals=3, overall_scores=[8.5, 9.0, 8.5])

    res_strong = client.get("/api/analytics/strong-areas", headers=headers2)
    assert res_strong.status_code == 200
    strong_data = res_strong.json()

    assert len(strong_data) > 0
    assert strong_data[0]["average_score"] == 8.7


# =========================================================
# 31 - 33. PRACTICE ACTIVITY & STREAK TESTS
# =========================================================

def test_31_to_33_practice_activity_and_streaks():
    user, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}

    seed_user_interview_with_evaluations(user, num_evals=2)

    res_act = client.get("/api/analytics/activity?days=30", headers=headers)
    assert res_act.status_code == 200
    act_data = res_act.json()
    assert len(act_data) > 0
    assert act_data[0]["questions_answered"] == 2

    res_ov = client.get("/api/analytics/overview", headers=headers)
    assert res_ov.status_code == 200
    assert res_ov.json()["current_streak"] >= 1


# =========================================================
# 34 & 35. VOICE VS TEXT ANALYTICS TESTS
# =========================================================

def test_34_and_35_voice_vs_text_counts():
    user, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}

    seed_user_interview_with_evaluations(user, num_evals=2, input_mode="VOICE")
    seed_user_interview_with_evaluations(user, num_evals=1, input_mode="TEXT")

    res = client.get("/api/analytics/overview", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["voice_answers"] == 2
    assert data["text_answers"] == 1
    assert data["voice_percentage"] == 66.7
    assert data["text_percentage"] == 33.3


# =========================================================
# 36. MULTI-TENANT ISOLATION TEST
# =========================================================

def test_36_user_isolation_analytics_data():
    user_a, token_a = create_test_user("user_a_iso@example.com", "User A")
    user_b, token_b = create_test_user("user_b_iso@example.com", "User B")

    seed_user_interview_with_evaluations(user_a, num_evals=5, overall_scores=[9.0]*5)
    seed_user_interview_with_evaluations(user_b, num_evals=1, overall_scores=[4.0])

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    res_a = client.get("/api/analytics/overview", headers=headers_a)
    res_b = client.get("/api/analytics/overview", headers=headers_b)

    assert res_a.json()["average_score"] == 9.0
    assert res_b.json()["average_score"] == 4.0
    assert res_a.json()["total_answers"] == 5
    assert res_b.json()["total_answers"] == 1


# =========================================================
# 37. COMBINED DASHBOARD ENDPOINT TEST
# =========================================================

def test_37_combined_dashboard_endpoint_works():
    user, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}

    seed_user_interview_with_evaluations(user, num_evals=2)

    res = client.get("/api/analytics/dashboard", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert "overview" in data
    assert "skills" in data
    assert "recent_trend" in data
    assert "topics" in data
    assert "adaptive" in data
    assert "weak_areas" in data
    assert "strong_areas" in data
    assert "recent_activity" in data
    assert "recent_interviews" in data
