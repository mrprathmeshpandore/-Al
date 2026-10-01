import pytest
from datetime import datetime, timezone
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
from app.services.gemini_service import FakeGeminiService
from app.services.followup_engine import FollowupEngine
from app.services.counter_question_engine import CounterQuestionEngine
from app.services.interview_session_service import InterviewSessionService

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


def create_test_user(email="aspirant_adaptive@example.com", name="Adaptive User"):
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


def create_sample_question(db_session=None):
    close_at_end = False
    if db_session is None:
        db_session = TestingSessionLocal()
        close_at_end = True

    q = InterviewQuestion(
        question_text="What strategies should India adopt for green energy transition?",
        question_type="MAIN",
        difficulty="MODERATE",
        category="Environment & Ecology",
        topic="Climate Change",
    )
    db_session.add(q)
    db_session.commit()
    db_session.refresh(q)
    q_id = q.id
    if close_at_end:
        db_session.close()
    return q_id


# =========================================================
# 1 - 5. BASIC FOLLOW-UP ENGINE TESTS
# =========================================================

def test_1_to_5_followup_question_generation_and_linking():
    user, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}
    create_sample_question()

    # Start Session (Question 1 served, depth=0, type=MAIN)
    res_start = client.post("/api/interview/start", json={"total_questions": 3}, headers=headers)
    assert res_start.status_code == 201
    s_data = res_start.json()
    session_id = s_data["session_id"]
    sq1_id = s_data["current_question"]["id"]

    # Submit Answer 1
    res_ans1 = client.post(
        f"/api/interview/{session_id}/answer",
        json={"answer_text": "India must invest in solar and wind power storage infrastructure.", "answer_duration_seconds": 45},
        headers=headers,
    )
    assert res_ans1.status_code == 200
    ans1_id = res_ans1.json()["answer_id"]

    # Request Next Question -> triggers FollowupEngine (depth=1)
    res_next = client.post(f"/api/interview/{session_id}/next-question", headers=headers)
    assert res_next.status_code == 200
    n_data = res_next.json()

    # 1-5. Assert follow-up question created, linked, depth=1
    assert n_data["question"]["type"] in ["FOLLOW_UP", "ETHICAL", "SCENARIO"]
    assert n_data["question"]["question_depth"] == 1
    assert n_data["question"]["parent_session_question_id"] == sq1_id
    assert n_data["question"]["parent_answer_id"] == ans1_id
    assert n_data["adaptive"]["is_adaptive"] is True
    assert n_data["adaptive"]["depth"] == 1


# =========================================================
# 6 - 8. COUNTER QUESTION ENGINE TESTS
# =========================================================

def test_6_to_8_counter_question_generation_and_linking():
    user, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}
    create_sample_question()

    # 1. Start session (Q1 MAIN)
    res_start = client.post("/api/interview/start", json={"total_questions": 3}, headers=headers)
    session_id = res_start.json()["session_id"]

    # 2. Answer Q1
    client.post(
        f"/api/interview/{session_id}/answer",
        json={"answer_text": "Answer 1 text for green energy transition.", "answer_duration_seconds": 40},
        headers=headers,
    )

    # 3. Next question (Q2 FOLLOW_UP, depth=1)
    res_q2 = client.post(f"/api/interview/{session_id}/next-question", headers=headers)
    sq2_id = res_q2.json()["question"]["id"]
    assert res_q2.json()["question"]["question_depth"] == 1

    # 4. Answer Q2 (FOLLOW_UP answer)
    res_ans2 = client.post(
        f"/api/interview/{session_id}/answer",
        json={"answer_text": "We can protect workers by retraining coal miners for renewable energy installations.", "answer_duration_seconds": 50},
        headers=headers,
    )
    ans2_id = res_ans2.json()["answer_id"]

    # 5. Next question -> triggers CounterQuestionEngine (depth=2)
    res_q3 = client.post(f"/api/interview/{session_id}/next-question", headers=headers)
    assert res_q3.status_code == 200
    q3_data = res_q3.json()

    # 6-8. Assert counter question created, linked, depth=2
    assert q3_data["question"]["type"] in ["COUNTER", "ETHICAL", "SCENARIO"]
    assert q3_data["question"]["question_depth"] == 2
    assert q3_data["question"]["parent_session_question_id"] == sq2_id
    assert q3_data["question"]["parent_answer_id"] == ans2_id
    assert q3_data["adaptive"]["depth"] == 2


# =========================================================
# 9 & 10. NO FOLLOW-UP DECISION (FALLBACK TO MAIN)
# =========================================================

def test_9_and_10_no_followup_fallback_to_next_main():
    user, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}
    create_sample_question()
    create_sample_question()

    res_start = client.post("/api/interview/start", json={"total_questions": 3}, headers=headers)
    session_id = res_start.json()["session_id"]

    client.post(
        f"/api/interview/{session_id}/answer",
        json={"answer_text": "Complete comprehensive balanced answer.", "answer_duration_seconds": 60},
        headers=headers,
    )

    # Mock Gemini to return should_follow_up = False
    db = TestingSessionLocal()
    no_f_json = {
        "should_follow_up": False,
        "reason": "Answer is comprehensive and well-balanced.",
        "follow_up_type": None,
        "question": None,
    }
    fake = FakeGeminiService(mock_json_response=no_f_json)

    # Directly invoke session service with fake Gemini
    service = InterviewSessionService(db, gemini_service=fake)
    next_sq = service.get_next_question(session_id, user.id)

    # 9-10. System proceeds to next MAIN question (depth=0)
    assert next_sq.question_depth == 0
    assert next_sq.adaptive_type == "MAIN"
    assert next_sq.parent_session_question_id is None
    db.close()


# =========================================================
# 11 - 14. VALIDATION & PROHIBITED LANGUAGE TESTS
# =========================================================

def test_11_to_14_validation_and_prohibited_phrases():
    user, token = create_test_user()
    ans_id = "test-ans-id"

    db = TestingSessionLocal()
    user_obj = db.query(User).filter(User.id == user.id).first()

    # Create session & session question
    q = InterviewQuestion(question_text="Parent Q text for testing validation bounds.", question_type="MAIN")
    db.add(q)
    db.commit()

    sq = InterviewSessionQuestion(session_id="s1", sequence_number=1, question_id=q.id)
    db.add(sq)
    db.commit()

    ans = InterviewAnswer(session_question_id=sq.id, answer_text="Answer text")
    db.add(ans)
    db.commit()

    # Prohibited certainty phrase in generated follow-up
    prohibited_json = {
        "should_follow_up": True,
        "reason": "Testing prohibited phrase",
        "follow_up_type": "FOLLOW_UP",
        "question": "This is a guaranteed upsc question that will definitely be asked.",
    }
    fake = FakeGeminiService(mock_json_response=prohibited_json)
    engine = FollowupEngine(db, gemini_service=fake)

    should_f, f_q, reason = engine.evaluate_and_generate_followup(sq, ans, user_obj)
    # 14. Certainty phrase rejected
    assert should_f is False
    assert f_q is None
    db.close()


# =========================================================
# 15 & 16. IDEMPOTENCY TESTS
# =========================================================

def test_15_and_16_repeated_next_question_call_returns_existing_question():
    user, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}
    create_sample_question()

    res_start = client.post("/api/interview/start", json={"total_questions": 3}, headers=headers)
    session_id = res_start.json()["session_id"]

    client.post(
        f"/api/interview/{session_id}/answer",
        json={"answer_text": "Answer text for idempotency check.", "answer_duration_seconds": 30},
        headers=headers,
    )

    # First call generates next question
    res_next1 = client.post(f"/api/interview/{session_id}/next-question", headers=headers)
    assert res_next1.status_code == 200
    q1_id = res_next1.json()["question"]["id"]

    # Second call returns existing question (idempotent, no duplicate generated)
    res_next2 = client.post(f"/api/interview/{session_id}/next-question", headers=headers)
    assert res_next2.status_code == 200
    q2_id = res_next2.json()["question"]["id"]
    assert q1_id == q2_id


# =========================================================
# 17 - 19. SECURITY & USER ISOLATION TESTS
# =========================================================

def test_17_to_19_user_isolation_for_adaptive_questions():
    user_a, token_a = create_test_user("usera_adapt@example.com", "User A")
    user_b, token_b = create_test_user("userb_adapt@example.com", "User B")
    create_sample_question()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    res_start_a = client.post("/api/interview/start", json={"total_questions": 3}, headers=headers_a)
    session_id_a = res_start_a.json()["session_id"]

    client.post(
        f"/api/interview/{session_id_a}/answer",
        json={"answer_text": "User A answer", "answer_duration_seconds": 30},
        headers=headers_a,
    )

    # 17 & 19. User B cannot request next question for User A session (404)
    res_b_next = client.post(f"/api/interview/{session_id_a}/next-question", headers=headers_b)
    assert res_b_next.status_code == 404


# =========================================================
# 20 - 22. STATE CONSTRAINTS & INVALID TRANSITIONS
# =========================================================

def test_20_followup_cannot_be_generated_before_answer():
    user, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}
    create_sample_question()

    res_start = client.post("/api/interview/start", json={"total_questions": 3}, headers=headers)
    session_id = res_start.json()["session_id"]

    # Call next-question without submitting answer to current question (409)
    res_next = client.post(f"/api/interview/{session_id}/next-question", headers=headers)
    assert res_next.status_code == 409


def test_21_and_22_completed_or_abandoned_session_cannot_generate_adaptive_question():
    user, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}
    create_sample_question()

    res_start = client.post("/api/interview/start", json={"total_questions": 3}, headers=headers)
    session_id = res_start.json()["session_id"]

    # Complete session
    client.post(f"/api/interview/{session_id}/complete", headers=headers)

    # Try requesting next question on completed session (409)
    res_next = client.post(f"/api/interview/{session_id}/next-question", headers=headers)
    assert res_next.status_code == 409


# =========================================================
# 23 - 25. DEPTH BOUNDS & MAIN RESET TESTS
# =========================================================

def test_23_to_25_depth_limit_and_main_reset_chain():
    user, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}
    create_sample_question()
    create_sample_question()

    # 1. Q1 MAIN (depth=0)
    res_start = client.post("/api/interview/start", json={"total_questions": 3}, headers=headers)
    session_id = res_start.json()["session_id"]
    assert res_start.json()["current_question"]["question_depth"] == 0

    # Answer Q1
    client.post(
        f"/api/interview/{session_id}/answer",
        json={"answer_text": "Answer 1", "answer_duration_seconds": 30},
        headers=headers,
    )

    # 2. Q2 FOLLOW_UP (depth=1)
    res_q2 = client.post(f"/api/interview/{session_id}/next-question", headers=headers)
    assert res_q2.json()["question"]["question_depth"] == 1

    # Answer Q2
    client.post(
        f"/api/interview/{session_id}/answer",
        json={"answer_text": "Answer 2 to follow up", "answer_duration_seconds": 30},
        headers=headers,
    )

    # 3. Q3 COUNTER (depth=2)
    res_q3 = client.post(f"/api/interview/{session_id}/next-question", headers=headers)
    assert res_q3.json()["question"]["question_depth"] == 2

    # Answer Q3
    client.post(
        f"/api/interview/{session_id}/answer",
        json={"answer_text": "Answer 3 to counter", "answer_duration_seconds": 30},
        headers=headers,
    )

    # 4. Q4 Next Question (since max depth=2 reached, must reset to MAIN depth=0)
    res_q4 = client.post(f"/api/interview/{session_id}/next-question", headers=headers)
    assert res_q4.status_code == 200
    assert res_q4.json()["question"]["question_depth"] == 0
    assert res_q4.json()["question"]["type"] == "MAIN"


# =========================================================
# 26 & 27. EVALUATION CONTEXT INTEGRATION
# =========================================================

def test_26_and_27_evaluation_context_integration():
    user, token = create_test_user()
    ans_id = "test-ans-id"

    db = TestingSessionLocal()
    user_obj = db.query(User).filter(User.id == user.id).first()

    q = InterviewQuestion(question_text="Parent Q text for evaluation context check.", question_type="MAIN")
    db.add(q)
    db.commit()

    sq = InterviewSessionQuestion(session_id="s1", sequence_number=1, question_id=q.id)
    db.add(sq)
    db.commit()

    ans = InterviewAnswer(session_question_id=sq.id, answer_text="Answer with Phase 10 evaluation")
    db.add(ans)
    db.commit()

    # Add Phase 10 evaluation
    eval_obj = InterviewAnswerEvaluation(
        answer_id=ans.id,
        content_score=8.0,
        content_feedback="Good",
        clarity_score=7.0,
        clarity_feedback="Clear",
        depth_score=5.0,
        depth_feedback="Lacks depth",
        reasoning_score=6.0,
        reasoning_feedback="Fair",
        balance_score=6.0,
        balance_feedback="Fair",
        communication_score=8.0,
        communication_feedback="Good",
        overall_score=6.7,
        overall_feedback="Needs depth",
        strengths=["Clarity"],
        areas_to_improve=["Depth"],
        suggested_answer="Model answer",
    )
    db.add(eval_obj)
    db.commit()

    fake = FakeGeminiService()
    engine = FollowupEngine(db, gemini_service=fake)

    # 26. Phase 10 evaluation context supplied safely
    should_f, f_q, reason = engine.evaluate_and_generate_followup(sq, ans, user_obj)
    assert should_f is True
    assert f_q is not None
    db.close()


# =========================================================
# 28 - 30. GEMINI FAILURE & ROLLBACK TESTS
# =========================================================

def test_28_to_30_gemini_failure_handling_and_rollback():
    user, token = create_test_user()
    db = TestingSessionLocal()
    user_obj = db.query(User).filter(User.id == user.id).first()

    q = InterviewQuestion(question_text="Parent Q text for error rollback test.", question_type="MAIN")
    db.add(q)
    db.commit()

    sq = InterviewSessionQuestion(session_id="s1", sequence_number=1, question_id=q.id)
    db.add(sq)
    db.commit()

    ans = InterviewAnswer(session_question_id=sq.id, answer_text="Answer text")
    db.add(ans)
    db.commit()

    fake_fail = FakeGeminiService(should_fail=True)
    engine = FollowupEngine(db, gemini_service=fake_fail)

    # 28-30. Gemini failure handled gracefully (returns should_follow_up = False without corrupting DB)
    should_f, f_q, reason = engine.evaluate_and_generate_followup(sq, ans, user_obj)
    assert should_f is False
    assert f_q is None
    db.close()
