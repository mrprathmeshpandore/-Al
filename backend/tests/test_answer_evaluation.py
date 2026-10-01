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
from app.services.answer_evaluation_service import AnswerEvaluationService, DIMENSION_WEIGHTS

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


def create_test_user(email="aspirant_eval@example.com", name="Aspirant Eval"):
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


def create_test_session_and_answer(user, answer_text="The Fourth Industrial Revolution requires proactive governance."):
    db = TestingSessionLocal()
    q = InterviewQuestion(
        question_text="How should India balance technology adoption with employment preservation?",
        question_type="MAIN",
        difficulty="MODERATE",
        category="Economy",
        topic="Governance",
    )
    db.add(q)
    db.commit()

    session = InterviewSession(
        user_id=user.id,
        status=SessionStatus.IN_PROGRESS.value,
        interview_type="FULL_INTERVIEW",
        total_questions=5,
        current_question_index=1,
    )
    db.add(session)
    db.commit()

    sq = InterviewSessionQuestion(
        session_id=session.id,
        question_id=q.id,
        sequence_number=1,
        question_status=QuestionSessionStatus.ANSWERED.value,
    )
    db.add(sq)
    db.commit()

    ans = InterviewAnswer(
        session_question_id=sq.id,
        answer_text=answer_text,
        answer_duration_seconds=60,
    )
    db.add(ans)
    db.commit()
    db.refresh(ans)
    ans_id = ans.id
    db.close()
    return ans_id


# =========================================================
# 1 & 2. AUTH TESTS
# =========================================================

def test_1_unauthenticated_evaluation_rejected():
    res = client.post("/api/interview/answers/dummy-answer-id/evaluate")
    assert res.status_code == 401

    res_get = client.get("/api/interview/answers/dummy-answer-id/evaluation")
    assert res_get.status_code == 401


def test_2_authenticated_evaluation_succeeds():
    user, token = create_test_user()
    ans_id = create_test_session_and_answer(user)
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post(f"/api/interview/answers/{ans_id}/evaluate", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["answer_id"] == ans_id
    assert "overall_score" in data
    assert "content" in data
    assert "clarity" in data


# =========================================================
# 3 & 4. OWNERSHIP ISOLATION TESTS
# =========================================================

def test_3_to_4_user_isolation():
    user_a, token_a = create_test_user("usera_eval@example.com", "User A")
    user_b, token_b = create_test_user("userb_eval@example.com", "User B")
    ans_id_a = create_test_session_and_answer(user_a)

    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B cannot evaluate User A answer (404)
    res_eval = client.post(f"/api/interview/answers/{ans_id_a}/evaluate", headers=headers_b)
    assert res_eval.status_code == 404

    # User B cannot get User A evaluation (404)
    res_get = client.get(f"/api/interview/answers/{ans_id_a}/evaluation", headers=headers_b)
    assert res_get.status_code == 404


# =========================================================
# 5 - 10. SCHEMA VALIDATION TESTS
# =========================================================

def test_5_valid_gemini_json_accepted():
    user, token = create_test_user()
    ans_id = create_test_session_and_answer(user)

    db = TestingSessionLocal()
    fake = FakeGeminiService()
    service = AnswerEvaluationService(db, gemini_service=fake)

    eval_obj = service.evaluate_answer(ans_id, user.id)
    assert eval_obj.answer_id == ans_id
    assert 0.0 <= eval_obj.overall_score <= 10.0
    db.close()


def test_6_malformed_json_rejected():
    user, token = create_test_user()
    ans_id = create_test_session_and_answer(user)

    db = TestingSessionLocal()
    fake = FakeGeminiService(should_malform=True)
    service = AnswerEvaluationService(db, gemini_service=fake)

    with pytest.raises(Exception) as excinfo:
        service.evaluate_answer(ans_id, user.id)
    assert "422" in str(excinfo.value) or "invalid" in str(excinfo.value).lower()
    db.close()


def test_7_missing_dimension_rejected():
    user, token = create_test_user()
    ans_id = create_test_session_and_answer(user)

    db = TestingSessionLocal()
    invalid_json = {
        "content": {"score": 8.0, "feedback": "Good"},
        # missing clarity, depth, reasoning, balance, communication
    }
    fake = FakeGeminiService(mock_json_response=invalid_json)
    service = AnswerEvaluationService(db, gemini_service=fake)

    with pytest.raises(Exception) as excinfo:
        service.evaluate_answer(ans_id, user.id)
    assert "422" in str(excinfo.value)
    db.close()


def test_8_and_9_score_out_of_bounds_rejected():
    user, token = create_test_user()
    ans_id = create_test_session_and_answer(user)

    db = TestingSessionLocal()
    base_valid = FakeGeminiService().generate_json_response("", "")

    # Score below 0 (-5)
    invalid_low = dict(base_valid)
    invalid_low["content"] = {"score": -5.0, "feedback": "Too low"}
    fake_low = FakeGeminiService(mock_json_response=invalid_low)
    service_low = AnswerEvaluationService(db, gemini_service=fake_low)

    with pytest.raises(Exception) as exc_low:
        service_low.evaluate_answer(ans_id, user.id)
    assert "422" in str(exc_low.value)

    # Score above 10 (15)
    invalid_high = dict(base_valid)
    invalid_high["content"] = {"score": 15.0, "feedback": "Too high"}
    fake_high = FakeGeminiService(mock_json_response=invalid_high)
    service_high = AnswerEvaluationService(db, gemini_service=fake_high)

    with pytest.raises(Exception) as exc_high:
        service_high.evaluate_answer(ans_id, user.id)
    assert "422" in str(exc_high.value)
    db.close()


def test_10_empty_feedback_rejected():
    user, token = create_test_user()
    ans_id = create_test_session_and_answer(user)

    db = TestingSessionLocal()
    base_valid = FakeGeminiService().generate_json_response("", "")
    invalid_empty = dict(base_valid)
    invalid_empty["content"] = {"score": 8.0, "feedback": ""}
    fake = FakeGeminiService(mock_json_response=invalid_empty)
    service = AnswerEvaluationService(db, gemini_service=fake)

    with pytest.raises(Exception) as excinfo:
        service.evaluate_answer(ans_id, user.id)
    assert "422" in str(excinfo.value)
    db.close()


# =========================================================
# 11 - 20. EVALUATION DIMENSIONS & BACKEND SCORE CALCULATION
# =========================================================

def test_11_to_20_dimension_scores_and_overall_backend_calculation():
    user, token = create_test_user()
    ans_id = create_test_session_and_answer(user)

    db = TestingSessionLocal()
    mock_res = {
        "content": {"score": 8.0, "feedback": "Accurate facts."},
        "clarity": {"score": 7.0, "feedback": "Good clarity."},
        "depth": {"score": 6.0, "feedback": "Moderate depth."},
        "reasoning": {"score": 9.0, "feedback": "Strong logic."},
        "balance": {"score": 7.0, "feedback": "Balanced views."},
        "communication": {"score": 8.0, "feedback": "Concise language."},
        "overall_feedback": "Overall solid performance.",
        "strengths": ["Logical structure", "Concise delivery"],
        "areas_to_improve": ["Deepen policy analysis"],
        "suggested_answer": "Model answer demonstrating structured reasoning...",
    }

    fake = FakeGeminiService(mock_json_response=mock_res)
    service = AnswerEvaluationService(db, gemini_service=fake)
    eval_obj = service.evaluate_answer(ans_id, user.id)

    # 11-16. All 6 dimension scores & feedbacks stored
    assert eval_obj.content_score == 8.0
    assert eval_obj.clarity_score == 7.0
    assert eval_obj.depth_score == 6.0
    assert eval_obj.reasoning_score == 9.0
    assert eval_obj.balance_score == 7.0
    assert eval_obj.communication_score == 8.0

    # 17. Authoritative Backend Calculation:
    # 8*0.2 + 7*0.15 + 6*0.2 + 9*0.2 + 7*0.15 + 8*0.1 = 1.6 + 1.05 + 1.2 + 1.8 + 1.05 + 0.8 = 7.5
    expected_overall = round(
        8.0 * 0.20 + 7.0 * 0.15 + 6.0 * 0.20 + 9.0 * 0.20 + 7.0 * 0.15 + 8.0 * 0.10, 2
    )
    assert eval_obj.overall_score == expected_overall
    assert eval_obj.overall_score == 7.5

    # 18-20. Strengths, areas_to_improve, suggested_answer stored
    assert eval_obj.strengths == ["Logical structure", "Concise delivery"]
    assert eval_obj.areas_to_improve == ["Deepen policy analysis"]
    assert "Model answer" in eval_obj.suggested_answer
    db.close()


# =========================================================
# 21 - 23. IDEMPOTENCY TESTS
# =========================================================

def test_21_to_23_idempotency_and_no_duplicate_gemini_calls():
    user, token = create_test_user()
    ans_id = create_test_session_and_answer(user)
    headers = {"Authorization": f"Bearer {token}"}

    # First call evaluates answer
    res1 = client.post(f"/api/interview/answers/{ans_id}/evaluate", headers=headers)
    assert res1.status_code == 200
    data1 = res1.json()
    eval_id1 = data1["id"]

    # Second call returns existing evaluation without error
    res2 = client.post(f"/api/interview/answers/{ans_id}/evaluate", headers=headers)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["id"] == eval_id1
    assert data2["overall_score"] == data1["overall_score"]

    # GET endpoint also returns exact same stored evaluation
    res_get = client.get(f"/api/interview/answers/{ans_id}/evaluation", headers=headers)
    assert res_get.status_code == 200
    assert res_get.json()["id"] == eval_id1


# =========================================================
# 24 - 26. ERROR HANDLING & ROLLBACK TESTS
# =========================================================

def test_24_to_26_gemini_failure_and_fallback():
    user, token = create_test_user()
    ans_id = create_test_session_and_answer(user)

    db = TestingSessionLocal()
    fake_fail = FakeGeminiService(should_fail=True)
    service = AnswerEvaluationService(db, gemini_service=fake_fail)

    # The service should catch the exception and fall back to FakeGeminiService
    eval_record = service.evaluate_answer(ans_id, user.id)

    # Verify an evaluation record was successfully created via fallback
    assert eval_record is not None
    assert eval_record.answer_id == ans_id
    
    # Verify the fallback values
    eval_in_db = db.query(InterviewAnswerEvaluation).filter(InterviewAnswerEvaluation.answer_id == ans_id).first()
    assert eval_in_db is not None
    db.close()


# =========================================================
# 27 - 29. SESSION & ANSWER VALIDITY TESTS
# =========================================================

def test_27_to_29_session_answer_validity():
    user, token = create_test_user()
    ans_id = create_test_session_and_answer(user)
    headers = {"Authorization": f"Bearer {token}"}

    # 28. Valid stored answer evaluated successfully
    res = client.post(f"/api/interview/answers/{ans_id}/evaluate", headers=headers)
    assert res.status_code == 200

    # 29. Invalid answer reference rejected (404)
    res_invalid = client.post("/api/interview/answers/non-existent-answer-id/evaluate", headers=headers)
    assert res_invalid.status_code == 404
