import io
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.config import settings, Settings
from app.core.database import Base, get_db
from app.models.user import User
from app.models.profile import UserProfile
from app.models.resource import Resource
from app.models.document import Document
from app.models.question import InterviewQuestion
from app.models.interview import (
    InterviewSession,
    InterviewSessionQuestion,
    InterviewAnswer,
    SessionStatus,
    QuestionSessionStatus,
)
from app.utils.security import create_access_token

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
        email=f"sec_user_a_{uuid.uuid4().hex[:6]}@example.com",
        full_name="Security User A",
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
        email=f"sec_user_b_{uuid.uuid4().hex[:6]}@example.com",
        full_name="Security User B",
        password_hash="hashed_secret_123",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_a(user_a):
    token = create_access_token(subject=user_a.id, email=user_a.email)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_b(user_b):
    token = create_access_token(subject=user_b.id, email=user_b.email)
    return {"Authorization": f"Bearer {token}"}


client = TestClient(app)


# ============================================================================
# 1-4. JWT SECURITY & AUTHENTICATION HARDENING TESTS
# ============================================================================
def test_security_01_missing_jwt_token_rejected():
    res = client.get("/api/profile")
    assert res.status_code == 401
    assert "detail" in res.json()


def test_security_02_invalid_jwt_token_rejected():
    res = client.get("/api/profile", headers={"Authorization": "Bearer invalid_token_format"})
    assert res.status_code == 401


def test_security_03_expired_jwt_token_rejected(user_a):
    past_time = datetime.now(timezone.utc) - timedelta(hours=2)
    expired_token = jwt.encode(
        {"sub": user_a.id, "email": user_a.email, "exp": past_time, "iat": past_time - timedelta(hours=1)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    res = client.get("/api/profile", headers={"Authorization": f"Bearer {expired_token}"})
    assert res.status_code == 401


def test_security_04_tampered_jwt_algorithm_none_rejected(user_a):
    # Attempt algorithm substitution / none attack
    tampered_token = jwt.encode(
        {"sub": user_a.id, "email": user_a.email, "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
        key="",
        algorithm="none",
    )
    res = client.get("/api/profile", headers={"Authorization": f"Bearer {tampered_token}"})
    assert res.status_code == 401


# ============================================================================
# 5-12. CROSS-USER AUTHORIZATION & IDOR ISOLATION TESTS
# ============================================================================
def test_security_05_cross_user_profile_isolation(auth_a, auth_b):
    res_a = client.get("/api/profile", headers=auth_a)
    assert res_a.status_code == 200
    assert res_a.json()["profile"]["personal"]["fullName"] == "Security User A"

    res_b = client.get("/api/profile", headers=auth_b)
    assert res_b.status_code == 200
    assert res_b.json()["profile"]["personal"]["fullName"] == "Security User B"


def test_security_06_cross_user_resource_and_document_access(db_session, user_a, auth_b):
    # Create private resource owned by User A
    res_obj = Resource(
        title="User A Confidential Policy Notes",
        category="Policy",
        subject="Governance",
        resource_type="pdf",
        is_official=False,
        created_by=user_a.id,
    )
    db_session.add(res_obj)
    db_session.commit()
    db_session.refresh(res_obj)

    # User B attempts to fetch User A's private resource detail & documents
    res_detail = client.get(f"/api/resources/{res_obj.id}", headers=auth_b)
    assert res_detail.status_code == 404

    res_docs = client.get(f"/api/resources/{res_obj.id}/documents", headers=auth_b)
    assert res_docs.status_code == 404


def test_security_07_cross_user_rag_chunks_isolation(db_session, user_a, auth_b):
    # Upload user A document
    pdf_bytes = b"%PDF-1.4 User A Private Document Content Article 370."
    pdf_file = ("user_a_private.pdf", io.BytesIO(pdf_bytes), "application/pdf")
    res_up = client.post(
        "/api/resources/upload",
        data={"title": "User A Private Doc", "category": "Polity", "subject": "Polity", "resource_type": "pdf"},
        files={"file": pdf_file},
        headers={"Authorization": f"Bearer {create_access_token(subject=user_a.id, email=user_a.email)}"},
    )
    assert res_up.status_code == 201

    # User B queries RAG knowledge base
    res_search = client.post(
        "/api/rag/search",
        json={"query": "Article 370", "top_k": 5},
        headers=auth_b,
    )
    assert res_search.status_code == 200
    results = res_search.json()["results"]
    for r in results:
        assert r["resource_title"] != "User A Private Doc"


def test_security_08_cross_user_interview_session_isolation(db_session, user_a, auth_b):
    session = InterviewSession(user_id=user_a.id, status=SessionStatus.IN_PROGRESS.value)
    db_session.add(session)
    db_session.commit()

    # User B attempts to access/answer User A's session
    res_fetch = client.get(f"/api/interview/{session.id}", headers=auth_b)
    assert res_fetch.status_code in (403, 404)


def test_security_09_cross_user_coach_plan_isolation(db_session, user_a, auth_b):
    res_plan_a = client.post("/api/coach/daily-plan", headers={"Authorization": f"Bearer {create_access_token(subject=user_a.id, email=user_a.email)}"})
    assert res_plan_a.status_code in (200, 201)
    plan_data = res_plan_a.json()
    plan_id = plan_data.get("id") or plan_data.get("plan", {}).get("id")
    assert plan_id is not None

    # User B attempts to read User A's coach plan
    res_access_b = client.get(f"/api/coach/plans/{plan_id}", headers=auth_b)
    assert res_access_b.status_code in (403, 404)


# ============================================================================
# 13-15. FILE UPLOAD & PATH TRAVERSAL SECURITY TESTS
# ============================================================================
def test_security_10_upload_invalid_mime_rejected(auth_a):
    fake_exe = ("malicious.exe", io.BytesIO(b"MZ executable bytes"), "application/x-msdownload")
    res = client.post(
        "/api/resources/upload",
        data={"title": "Malicious Executable", "category": "General", "subject": "General", "resource_type": "pdf"},
        files={"file": fake_exe},
        headers=auth_a,
    )
    assert res.status_code == 400


def test_security_11_upload_oversized_pdf_rejected(auth_a):
    # 26MB dummy file exceeding 25MB MAX_PDF_SIZE_MB
    oversized_bytes = b"0" * (26 * 1024 * 1024)
    big_file = ("huge.pdf", io.BytesIO(oversized_bytes), "application/pdf")
    res = client.post(
        "/api/resources/upload",
        data={"title": "Oversized Document", "category": "General", "subject": "General", "resource_type": "pdf"},
        files={"file": big_file},
        headers=auth_a,
    )
    assert res.status_code == 400
    assert "exceeds" in res.json()["detail"].lower()


def test_security_12_upload_path_traversal_filename_sanitized(auth_a):
    traversal_file = ("../../../../etc/passwd.pdf", io.BytesIO(b"%PDF-1.4 Safe PDF"), "application/pdf")
    res = client.post(
        "/api/resources/upload",
        data={"title": "Traversal Test", "category": "General", "subject": "General", "resource_type": "pdf"},
        files={"file": traversal_file},
        headers=auth_a,
    )
    assert res.status_code == 201
    doc_id = res.json()["document_id"]
    db = TestingSessionLocal()
    doc = db.query(Document).filter(Document.id == doc_id).first()
    assert "../" not in doc.stored_filename
    assert "/" not in doc.stored_filename
    db.close()


# ============================================================================
# 16-20. SENSITIVE ERROR RESPONSE & PRODUCTION CONFIGURATION TESTS
# ============================================================================
def test_security_13_sensitive_error_response_prevention(auth_a):
    # Invalid endpoint trigger or unhandled database query
    res = client.get("/api/questions/non_existent_uuid_12345", headers=auth_a)
    assert res.status_code == 404
    # Ensure internal SQL or python stacktraces are not exposed in response detail
    body_str = res.text
    assert "Traceback" not in body_str
    assert "SELECT " not in body_str
    assert "sqlite3" not in body_str


def test_security_14_security_response_headers_present():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "DENY"
    assert res.headers.get("X-XSS-Protection") == "1; mode=block"


def test_security_15_production_config_rejects_weak_secret():
    prod_settings = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="dev_secret_key_prashasak_ai_change_in_production_32bytes",
        CORS_ORIGINS=["http://localhost:5173"],
    )
    with pytest.raises(ValueError, match="SECRET_KEY must be a non-default string"):
        prod_settings.check_production_security()


def test_security_16_production_config_rejects_wildcard_cors():
    prod_settings = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="a_super_strong_production_secret_key_32bytes_min_length_value",
        CORS_ORIGINS=["*"],
    )
    with pytest.raises(ValueError, match="Wildcard '\\*' origins are not allowed"):
        prod_settings.check_production_security()
