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


def create_test_user(email="aspirant1@example.com", name="Aspirant One"):
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
        question_text="What are your views on Administrative Reforms in India?",
        question_type="MAIN",
        difficulty="MODERATE",
        category="Polity & Governance",
        topic="Governance",
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    q_id = q.id
    db.close()
    return q_id


# =========================================================
# 1 & 2. AUTH TESTS
# =========================================================

def test_1_unauthenticated_start_rejected():
    res = client.post("/api/interview/start", json={"total_questions": 5})
    assert res.status_code == 401


def test_2_authenticated_user_can_start_interview():
    user, token = create_test_user()
    create_sample_question()
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/interview/start", json={"total_questions": 5, "interview_type": "FULL_INTERVIEW"}, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert "session_id" in data
    assert data["status"] == "IN_PROGRESS"
    assert data["total_questions"] == 5
    assert data["current_question_index"] == 1
    assert data["current_question"] is not None


# =========================================================
# 3 - 7. SESSION TESTS
# =========================================================

def test_3_to_7_session_creation_and_retrieval():
    user, token = create_test_user()
    create_sample_question()
    headers = {"Authorization": f"Bearer {token}"}

    # Start session
    start_res = client.post("/api/interview/start", json={"total_questions": 3, "interview_type": "QUICK_PRACTICE"}, headers=headers)
    assert start_res.status_code == 201
    s_data = start_res.json()
    session_id = s_data["session_id"]

    # 3 & 4. Session created & in IN_PROGRESS state
    assert s_data["status"] == "IN_PROGRESS"
    # 5. Total question count matches
    assert s_data["total_questions"] == 3
    # 6. First question attached
    assert s_data["current_question"] is not None
    assert s_data["current_question"]["sequence_number"] == 1

    # 7. Session can be retrieved
    get_res = client.get(f"/api/interview/{session_id}", headers=headers)
    assert get_res.status_code == 200
    g_data = get_res.json()
    assert g_data["session_id"] == session_id
    assert g_data["interview_type"] == "QUICK_PRACTICE"


# =========================================================
# 8 - 10. SECURITY TESTS (User Isolation)
# =========================================================

def test_8_to_10_user_isolation():
    user_a, token_a = create_test_user("usera@example.com", "User A")
    user_b, token_b = create_test_user("userb@example.com", "User B")
    create_sample_question()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A starts session
    res_a = client.post("/api/interview/start", json={"total_questions": 3}, headers=headers_a)
    session_id_a = res_a.json()["session_id"]

    # 8. User B cannot get User A session (404)
    res_get_b = client.get(f"/api/interview/{session_id_a}", headers=headers_b)
    assert res_get_b.status_code == 404

    # 9. User B cannot submit answer to User A session (404)
    res_ans_b = client.post(
        f"/api/interview/{session_id_a}/answer",
        json={"answer_text": "Unauthorized answer", "answer_duration_seconds": 30},
        headers=headers_b,
    )
    assert res_ans_b.status_code == 404

    # 10. User B cannot complete User A session (404)
    res_comp_b = client.post(f"/api/interview/{session_id_a}/complete", headers=headers_b)
    assert res_comp_b.status_code == 404


# =========================================================
# 11 - 15. ANSWER SUBMISSION TESTS
# =========================================================

def test_11_valid_answer_stored():
    user, token = create_test_user()
    create_sample_question()
    headers = {"Authorization": f"Bearer {token}"}

    res_start = client.post("/api/interview/start", json={"total_questions": 2}, headers=headers)
    session_id = res_start.json()["session_id"]

    res_ans = client.post(
        f"/api/interview/{session_id}/answer",
        json={"answer_text": "Reforms should focus on transparency and digitization.", "answer_duration_seconds": 45},
        headers=headers,
    )
    assert res_ans.status_code == 200
    data = res_ans.json()
    assert "answer_id" in data
    assert data["next_action"] == "NEXT_QUESTION"


def test_12_empty_answer_rejected():
    user, token = create_test_user()
    create_sample_question()
    headers = {"Authorization": f"Bearer {token}"}

    res_start = client.post("/api/interview/start", json={"total_questions": 2}, headers=headers)
    session_id = res_start.json()["session_id"]

    res_ans = client.post(
        f"/api/interview/{session_id}/answer",
        json={"answer_text": "   ", "answer_duration_seconds": 10},
        headers=headers,
    )
    assert res_ans.status_code in [422, 400]


def test_13_invalid_duration_rejected():
    user, token = create_test_user()
    create_sample_question()
    headers = {"Authorization": f"Bearer {token}"}

    res_start = client.post("/api/interview/start", json={"total_questions": 2}, headers=headers)
    session_id = res_start.json()["session_id"]

    res_ans = client.post(
        f"/api/interview/{session_id}/answer",
        json={"answer_text": "Valid text", "answer_duration_seconds": -5},
        headers=headers,
    )
    assert res_ans.status_code == 422


def test_14_duplicate_answer_rejected():
    user, token = create_test_user()
    create_sample_question()
    headers = {"Authorization": f"Bearer {token}"}

    res_start = client.post("/api/interview/start", json={"total_questions": 2}, headers=headers)
    session_id = res_start.json()["session_id"]

    # Submit first time
    client.post(
        f"/api/interview/{session_id}/answer",
        json={"answer_text": "First answer text", "answer_duration_seconds": 30},
        headers=headers,
    )

    # Duplicate submission
    res_ans2 = client.post(
        f"/api/interview/{session_id}/answer",
        json={"answer_text": "Second answer text", "answer_duration_seconds": 30},
        headers=headers,
    )
    assert res_ans2.status_code == 409


def test_15_completed_session_cannot_accept_answer():
    user, token = create_test_user()
    create_sample_question()
    headers = {"Authorization": f"Bearer {token}"}

    res_start = client.post("/api/interview/start", json={"total_questions": 2}, headers=headers)
    session_id = res_start.json()["session_id"]

    # Complete session directly
    client.post(f"/api/interview/{session_id}/complete", headers=headers)

    # Try answering
    res_ans = client.post(
        f"/api/interview/{session_id}/answer",
        json={"answer_text": "Late answer", "answer_duration_seconds": 20},
        headers=headers,
    )
    assert res_ans.status_code == 409


# =========================================================
# 16 - 19. NEXT QUESTION TESTS
# =========================================================

def test_16_to_19_next_question_flow():
    user, token = create_test_user()
    create_sample_question()
    headers = {"Authorization": f"Bearer {token}"}

    # Start 2-question interview (non-adaptive for sequence test)
    res_start = client.post("/api/interview/start", json={"total_questions": 2, "include_adaptive": False}, headers=headers)
    session_id = res_start.json()["session_id"]

    # Submit answer 1
    res_a1 = client.post(
        f"/api/interview/{session_id}/answer",
        json={"answer_text": "Answer 1", "answer_duration_seconds": 25},
        headers=headers,
    )
    assert res_a1.json()["next_action"] == "NEXT_QUESTION"

    # Fetch next question
    res_q2 = client.post(f"/api/interview/{session_id}/next-question", headers=headers)
    assert res_q2.status_code == 200
    q2_data = res_q2.json()
    assert q2_data["progress"]["current"] == 2
    assert q2_data["progress"]["total"] == 2
    assert q2_data["question"]["sequence_number"] == 2

    # Submit answer 2 (final question)
    res_a2 = client.post(
        f"/api/interview/{session_id}/answer",
        json={"answer_text": "Answer 2", "answer_duration_seconds": 40},
        headers=headers,
    )
    assert res_a2.json()["next_action"] == "COMPLETE_INTERVIEW"

    # Try fetching next question when all questions done (409)
    res_q3 = client.post(f"/api/interview/{session_id}/next-question", headers=headers)
    assert res_q3.status_code == 409


# =========================================================
# 20 - 22. COMPLETE SESSION TESTS
# =========================================================

def test_20_to_22_complete_session():
    user, token = create_test_user()
    create_sample_question()
    headers = {"Authorization": f"Bearer {token}"}

    res_start = client.post("/api/interview/start", json={"total_questions": 2}, headers=headers)
    session_id = res_start.json()["session_id"]

    # Submit answer 1
    client.post(
        f"/api/interview/{session_id}/answer",
        json={"answer_text": "Answer 1", "answer_duration_seconds": 20},
        headers=headers,
    )

    # 20 & 21. Complete session
    res_comp = client.post(f"/api/interview/{session_id}/complete", headers=headers)
    assert res_comp.status_code == 200
    comp_data = res_comp.json()
    assert comp_data["status"] == "COMPLETED"
    assert comp_data["completed_at"] is not None
    assert comp_data["answered_questions"] == 1

    # 22. Completed session rejects further operations
    res_next = client.post(f"/api/interview/{session_id}/next-question", headers=headers)
    assert res_next.status_code == 409


# =========================================================
# 23 - 25. HISTORY TESTS
# =========================================================

def test_23_to_25_interview_history():
    user1, token1 = create_test_user("hist1@example.com", "History User 1")
    user2, token2 = create_test_user("hist2@example.com", "History User 2")
    create_sample_question()

    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}

    # User 1 starts 3 sessions
    client.post("/api/interview/start", json={"total_questions": 3, "interview_type": "FULL_INTERVIEW"}, headers=headers1)
    client.post("/api/interview/start", json={"total_questions": 5, "interview_type": "QUICK_PRACTICE"}, headers=headers1)
    client.post("/api/interview/start", json={"total_questions": 2, "interview_type": "DAF_INTERVIEW"}, headers=headers1)

    # User 2 starts 1 session
    client.post("/api/interview/start", json={"total_questions": 4}, headers=headers2)

    # 23. Authenticated history returned for User 1
    res_h1 = client.get("/api/interview/history", headers=headers1)
    assert res_h1.status_code == 200
    data_h1 = res_h1.json()
    # 25. Only User 1 sessions returned
    assert data_h1["total"] == 3
    assert len(data_h1["items"]) == 3

    # 24. Pagination works
    res_p1 = client.get("/api/interview/history?page=1&page_size=2", headers=headers1)
    assert res_p1.status_code == 200
    data_p1 = res_p1.json()
    assert len(data_p1["items"]) == 2
    assert data_p1["pages"] == 2

    # User 2 history
    res_h2 = client.get("/api/interview/history", headers=headers2)
    assert res_h2.status_code == 200
    assert res_h2.json()["total"] == 1


# =========================================================
# 26 - 28. STATE MACHINE & INVALID TRANSITIONS
# =========================================================

def test_26_invalid_start_config_rejected():
    user, token = create_test_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Unsupported interview_type
    res1 = client.post("/api/interview/start", json={"interview_type": "INVALID_TYPE"}, headers=headers)
    assert res1.status_code == 422

    # Invalid question count (> 20)
    res2 = client.post("/api/interview/start", json={"total_questions": 99}, headers=headers)
    assert res2.status_code == 422


def test_27_abandoned_session_cannot_continue():
    user, token = create_test_user()
    db = TestingSessionLocal()

    # Manually mark session as ABANDONED
    session = InterviewSession(
        user_id=user.id,
        status=SessionStatus.ABANDONED.value,
        interview_type="FULL_INTERVIEW",
        total_questions=5,
        current_question_index=1,
    )
    db.add(session)
    db.commit()
    s_id = session.id
    db.close()

    token = create_access_token(user.id, user.email)
    headers = {"Authorization": f"Bearer {token}"}

    res_ans = client.post(
        f"/api/interview/{s_id}/answer",
        json={"answer_text": "Test answer", "answer_duration_seconds": 10},
        headers=headers,
    )
    assert res_ans.status_code == 409

    res_comp = client.post(f"/api/interview/{s_id}/complete", headers=headers)
    assert res_comp.status_code == 409


def test_28_completed_session_cannot_continue():
    user, token = create_test_user()
    create_sample_question()
    headers = {"Authorization": f"Bearer {token}"}

    res_start = client.post("/api/interview/start", json={"total_questions": 2}, headers=headers)
    s_id = res_start.json()["session_id"]

    client.post(f"/api/interview/{s_id}/complete", headers=headers)

    res_next = client.post(f"/api/interview/{s_id}/next-question", headers=headers)
    assert res_next.status_code == 409
