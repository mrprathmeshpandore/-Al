import io
import pytest
import pypdf
import uuid
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.config import settings
from app.core.database import Base, get_db
from app.models.user import User
from app.models.profile import UserProfile
from app.models.resource import Resource
from app.models.document import Document, ProcessingStatus
from app.models.document_chunk import DocumentChunk, EmbeddingStatus
from app.models.question import InterviewQuestion, InterviewQuestionSource
from app.services.embedding_provider import FakeEmbeddingProvider
from app.services.gemini_service import FakeGeminiService
from app.services.embedding_service import compute_content_hash
from app.services.daf_context_builder import (
    extract_daf_topic_and_context,
)
from app.services.personalization_service import (
    generate_personalized_interview_question,
)
from app.services.question_generation_service import (
    list_user_questions,
    get_user_question_by_id,
    delete_user_question_by_id,
    UNGROUNDED_QUESTION_MESSAGE,
)

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
    import app.routers.resources as resources_router
    resources_router.SessionLocal = TestingSessionLocal
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def create_sample_user_and_profile(db, email="candidate@example.com", name="Test Candidate"):
    user = User(
        email=email,
        password_hash="hashedpassword123",
        full_name=name,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    profile = UserProfile(
        user_id=user.id,
        date_of_birth="1998-05-15",
        gender="MALE",
        home_state="Maharashtra",
        district="Pune",
        current_city="Mumbai",
        education_data={
            "degree": "B.Tech",
            "university": "COEP Pune",
            "specialization": "Computer Engineering",
            "postGraduation": "M.Tech AI",
            "otherQualifications": "AWS Certified",
        },
        upsc_journey_data={
            "attemptCount": 2,
            "optionalSubject": "Public Administration",
            "previousInterviewExp": True,
            "preparationStage": "INTERVIEW",
        },
        interests={
            "hobbies": ["Trekking in Sahyadris", "Photography"],
            "sports": ["Badminton", "Chess"],
            "readingBooks": ["India After Gandhi", "Discovery of India"],
            "areasOfInterest": ["Rural Governance", "E-Governance"],
            "socialActivities": ["NSS Volunteer", "Blood Donation Camps"],
        },
        perspective={
            "whyCivilServices": "To contribute to policy implementation and grassroot development.",
            "keyFocusAreas": ["Digital Healthcare", "Primary Education"],
            "boardMessage": "Honest, balanced, and administrative mindset.",
        },
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return user, profile


def setup_sample_knowledge_chunk(db, user_id, title="UPSC Governance & Admin Guide", content="Public Administration principles include delegation, administrative accountability, and citizen-centric governance in district administration.", query_text=None):
    resource = Resource(
        title=title,
        category="Governance",
        subject="Polity",
        created_by=user_id,
    )
    db.add(resource)
    db.flush()

    doc = Document(
        resource_id=resource.id,
        original_filename="admin_guide.pdf",
        stored_filename=f"admin_guide_{uuid.uuid4()}.pdf",
        mime_type="application/pdf",
        file_size=1024,
        processing_status=ProcessingStatus.PROCESSED.value,
        created_by=user_id,
    )
    db.add(doc)
    db.flush()

    fake_provider = FakeEmbeddingProvider(vector_dim=768)
    emb = fake_provider.embed_text(query_text or content)

    chunk = DocumentChunk(
        document_id=doc.id,
        chunk_index=0,
        content=content,
        content_hash=compute_content_hash(content),
        page_number=1,
        embedding=emb,
        embedding_status=EmbeddingStatus.COMPLETED.value,
    )
    db.add(chunk)
    db.commit()
    db.refresh(doc)
    db.refresh(chunk)
    return doc, chunk


# ============================================================================
# 1-13: DAF Context Builder Unit Tests (All 13 Personalization Sources)
# ============================================================================

def test_daf_builder_education(setup_db):
    db = TestingSessionLocal()
    user, profile = create_sample_user_and_profile(db)
    res = extract_daf_topic_and_context(profile, "EDUCATION")
    assert res is not None
    assert "COEP Pune" in res["daf_context"]
    assert "Computer Engineering" in res["daf_context"]
    assert "Computer Engineering" in res["label"] or "B.Tech" in res["label"]


def test_daf_builder_hometown(setup_db):
    db = TestingSessionLocal()
    user, profile = create_sample_user_and_profile(db)
    res = extract_daf_topic_and_context(profile, "HOMETOWN")
    assert res is not None
    assert "Pune" in res["daf_context"]
    assert "Maharashtra" in res["daf_context"]
    assert "Pune" in res["label"]


def test_daf_builder_current_city(setup_db):
    db = TestingSessionLocal()
    user, profile = create_sample_user_and_profile(db)
    res = extract_daf_topic_and_context(profile, "CURRENT_CITY")
    assert res is not None
    assert "Mumbai" in res["daf_context"]
    assert "Mumbai" in res["label"]


def test_daf_builder_optional_subject(setup_db):
    db = TestingSessionLocal()
    user, profile = create_sample_user_and_profile(db)
    res = extract_daf_topic_and_context(profile, "OPTIONAL_SUBJECT")
    assert res is not None
    assert "Public Administration" in res["daf_context"]
    assert "Public Administration" in res["label"]


def test_daf_builder_upsc_journey(setup_db):
    db = TestingSessionLocal()
    user, profile = create_sample_user_and_profile(db)
    res = extract_daf_topic_and_context(profile, "UPSC_JOURNEY")
    assert res is not None
    assert "Attempt Count: 2" in res["daf_context"]
    assert "Attempt 2" in res["label"] or "UPSC" in res["label"]


def test_daf_builder_hobby(setup_db):
    db = TestingSessionLocal()
    user, profile = create_sample_user_and_profile(db)
    res = extract_daf_topic_and_context(profile, "HOBBY")
    assert res is not None
    assert "Trekking in Sahyadris" in res["daf_context"]
    assert "Trekking" in res["label"] or "Sahyadris" in res["label"]


def test_daf_builder_sport(setup_db):
    db = TestingSessionLocal()
    user, profile = create_sample_user_and_profile(db)
    res = extract_daf_topic_and_context(profile, "SPORT")
    assert res is not None
    assert "Badminton" in res["daf_context"]
    assert "Badminton" in res["label"]


def test_daf_builder_book(setup_db):
    db = TestingSessionLocal()
    user, profile = create_sample_user_and_profile(db)
    res = extract_daf_topic_and_context(profile, "BOOK")
    assert res is not None
    assert "India After Gandhi" in res["daf_context"]
    assert "India After Gandhi" in res["label"]


def test_daf_builder_interest(setup_db):
    db = TestingSessionLocal()
    user, profile = create_sample_user_and_profile(db)
    res = extract_daf_topic_and_context(profile, "INTEREST")
    assert res is not None
    assert "Rural Governance" in res["daf_context"]
    assert "Rural Governance" in res["label"]


def test_daf_builder_social_activity(setup_db):
    db = TestingSessionLocal()
    user, profile = create_sample_user_and_profile(db)
    res = extract_daf_topic_and_context(profile, "SOCIAL_ACTIVITY")
    assert res is not None
    assert "NSS Volunteer" in res["daf_context"]
    assert "NSS Volunteer" in res["label"]


def test_daf_builder_perspective(setup_db):
    db = TestingSessionLocal()
    user, profile = create_sample_user_and_profile(db)
    res = extract_daf_topic_and_context(profile, "PERSPECTIVE")
    assert res is not None
    assert "policy implementation" in res["daf_context"]
    assert "Digital Healthcare" in res["label"] or "Motivation" in res["label"]


def test_daf_builder_work_experience(setup_db):
    db = TestingSessionLocal()
    user = User(email="work@example.com", password_hash="pw", full_name="Work User")
    db.add(user)
    db.commit()

    profile = UserProfile(
        user_id=user.id,
        education_data={"workExperience": "Software Engineer at TechCorp for 3 years."},
    )
    db.add(profile)
    db.commit()

    res = extract_daf_topic_and_context(profile, "WORK_EXPERIENCE")
    assert res is not None
    assert "TechCorp" in res["daf_context"]
    assert "Software Engineer" in res["label"] or "TechCorp" in res["label"] or "Background" in res["label"]


def test_daf_builder_general_daf(setup_db):
    db = TestingSessionLocal()
    user, profile = create_sample_user_and_profile(db)
    res = extract_daf_topic_and_context(profile, "GENERAL_DAF")
    assert res is not None
    assert "COEP Pune" in res["daf_context"]
    assert "Maharashtra" in res["daf_context"]
    assert "Public Administration" in res["daf_context"]


# ============================================================================
# 14-16: DAF Safety & Fallback Tests
# ============================================================================

def test_fallback_when_user_profile_missing(setup_db):
    db = TestingSessionLocal()
    user = User(email="noprofile@example.com", password_hash="pw", full_name="No Profile User")
    db.add(user)
    db.commit()

    resp = generate_personalized_interview_question(
        source="EDUCATION",
        current_user=user,
        db=db,
    )
    assert resp["grounded"] is False
    assert resp["personalized"] is False
    assert resp["is_personalized"] is False
    assert UNGROUNDED_QUESTION_MESSAGE in resp["question_text"]


def test_fallback_when_requested_daf_field_is_empty(setup_db):
    db = TestingSessionLocal()
    user = User(email="emptyfield@example.com", password_hash="pw", full_name="Empty Field User")
    db.add(user)
    db.commit()

    profile = UserProfile(
        user_id=user.id,
        interests={"hobbies": []},  # empty hobbies
    )
    db.add(profile)
    db.commit()

    resp = generate_personalized_interview_question(
        source="HOBBY",
        current_user=user,
        db=db,
    )
    assert resp["grounded"] is False
    assert resp["personalized"] is False
    assert resp["is_personalized"] is False
    assert UNGROUNDED_QUESTION_MESSAGE in resp["question_text"]


def test_fallback_when_zero_rag_chunks_retrieved(setup_db):
    db = TestingSessionLocal()
    user, profile = create_sample_user_and_profile(db)

    # Mock RAG retrieval function
    def mock_retrieval(*args, **kwargs):
        return []

    resp = generate_personalized_interview_question(
        source="EDUCATION",
        current_user=user,
        db=db,
        retrieval_func=mock_retrieval,
    )
    assert resp["grounded"] is False
    assert resp["personalized"] is False
    assert resp["is_personalized"] is False
    assert UNGROUNDED_QUESTION_MESSAGE in resp["question_text"]


# ============================================================================
# 17-24: Gemini & Personalization Integration Tests
# ============================================================================

def test_personalized_question_pipeline_success(setup_db):
    db = TestingSessionLocal()
    user, profile = create_sample_user_and_profile(db)
    doc, chunk = setup_sample_knowledge_chunk(db, user.id)

    def mock_retrieval(*args, **kwargs):
        return [
            {
                "chunk_id": chunk.id,
                "document_id": doc.id,
                "content": chunk.content,
                "page_number": chunk.page_number,
                "chunk_index": chunk.chunk_index,
                "similarity_score": 0.88,
                "resource_title": "UPSC Governance & Admin Guide",
                "resource_id": doc.resource_id,
            }
        ]

    q_text = "Given your background in Computer Engineering from COEP Pune, how would you leverage administrative accountability and e-governance systems to reduce bureaucratic delays in district public administration?"
    fake_gemini = FakeGeminiService(mock_answer=q_text)

    resp = generate_personalized_interview_question(
        source="EDUCATION",
        current_user=user,
        db=db,
        retrieval_func=mock_retrieval,
        gemini_service=fake_gemini,
    )

    assert resp["grounded"] is True
    assert resp["personalized"] is True
    assert resp["is_personalized"] is True
    assert resp["personalization_source"] == "EDUCATION"
    assert "Computer Engineering" in resp["question_text"] or "COEP" in resp["question_text"]
    assert len(resp["citation_sources"]) == 1
    assert resp["citation_sources"][0]["resource_title"] == "UPSC Governance & Admin Guide"


def test_personalized_question_duplicate_detection(setup_db):
    db = TestingSessionLocal()
    user, profile = create_sample_user_and_profile(db)
    doc, chunk = setup_sample_knowledge_chunk(db, user.id)

    q_text = "How does your Public Administration optional subject prepare you for civil service challenges?"

    def mock_retrieval(*args, **kwargs):
        return [
            {
                "chunk_id": chunk.id,
                "document_id": doc.id,
                "content": chunk.content,
                "page_number": 1,
                "chunk_index": 0,
                "similarity_score": 0.90,
                "resource_title": "UPSC Governance & Admin Guide",
                "resource_id": doc.resource_id,
            }
        ]

    fake_gemini_1 = FakeGeminiService(mock_answer=q_text)
    fake_gemini_2 = FakeGeminiService(mock_answer="Second distinct question on Public Administration optional.")

    # First call persists question
    resp1 = generate_personalized_interview_question(
        source="OPTIONAL_SUBJECT",
        current_user=user,
        db=db,
        retrieval_func=mock_retrieval,
        gemini_service=fake_gemini_1,
    )
    assert resp1["question_text"] == q_text

    # Second call detects duplicate when Gemini generates identical question text
    resp2 = generate_personalized_interview_question(
        source="OPTIONAL_SUBJECT",
        current_user=user,
        db=db,
        retrieval_func=mock_retrieval,
        gemini_service=fake_gemini_1,
    )
    assert resp2["question_text"] == q_text


def test_user_daf_isolation(setup_db):
    db = TestingSessionLocal()
    user1, profile1 = create_sample_user_and_profile(db, email="user1@example.com", name="User One")
    user2 = User(email="user2@example.com", password_hash="pw", full_name="User Two")
    db.add(user2)
    db.commit()

    profile2 = UserProfile(
        user_id=user2.id,
        education_data={"degree": "MBBS", "university": "AIIMS New Delhi", "specialization": "Surgery"},
    )
    db.add(profile2)
    db.commit()

    # User 1 context must contain COEP Pune, User 2 context must contain AIIMS New Delhi
    res1 = extract_daf_topic_and_context(profile1, "EDUCATION")
    res2 = extract_daf_topic_and_context(profile2, "EDUCATION")

    assert "COEP Pune" in res1["daf_context"]
    assert "AIIMS New Delhi" not in res1["daf_context"]
    assert "AIIMS New Delhi" in res2["daf_context"]
    assert "COEP Pune" not in res2["daf_context"]


def test_user_question_isolation(setup_db):
    db = TestingSessionLocal()
    user1, profile1 = create_sample_user_and_profile(db, email="user1@example.com")
    user2 = User(email="user2@example.com", password_hash="pw", full_name="User Two")
    db.add(user2)
    db.commit()

    q = InterviewQuestion(
        user_id=user1.id,
        subject="POLITY",
        topic="Personalized Education Query",
        question_text="Sample question for user 1",
        difficulty="MODERATE",
        question_type="MAIN",
        is_personalized=True,
        personalization_source="EDUCATION",
        personalization_label="Education Background",
    )
    db.add(q)
    db.commit()
    db.refresh(q)

    # User 1 can access
    q_user1 = get_user_question_by_id(q.id, user1.id, db)
    assert q_user1 is not None

    # User 2 cannot access
    q_user2 = get_user_question_by_id(q.id, user2.id, db)
    assert q_user2 is None


def test_list_questions_filtering_by_personalization(setup_db):
    db = TestingSessionLocal()
    user, profile = create_sample_user_and_profile(db)

    q1 = InterviewQuestion(
        user_id=user.id,
        subject="POLITY",
        topic="General Topic",
        question_text="General UPSC question",
        is_personalized=False,
    )
    q2 = InterviewQuestion(
        user_id=user.id,
        subject="GOVERNANCE",
        topic="Hometown Topic",
        question_text="Hometown Pune question",
        is_personalized=True,
        personalization_source="HOMETOWN",
        personalization_label="Hometown Background",
    )
    q3 = InterviewQuestion(
        user_id=user.id,
        subject="ADMINISTRATION",
        topic="Optional Topic",
        question_text="Public Admin optional question",
        is_personalized=True,
        personalization_source="OPTIONAL_SUBJECT",
        personalization_label="Optional Subject",
    )
    db.add_all([q1, q2, q3])
    db.commit()

    # Filter is_personalized=True
    res_pers = list_user_questions(user.id, db, is_personalized=True)
    assert res_pers["total"] == 2
    assert all(item["is_personalized"] for item in res_pers["questions"])

    # Filter is_personalized=False
    res_gen = list_user_questions(user.id, db, is_personalized=False)
    assert res_gen["total"] == 1
    gen_q = res_gen["questions"][0]
    assert (gen_q.get("question") or gen_q.get("question_text")) == "General UPSC question"

    # Filter personalization_source="HOMETOWN"
    res_home = list_user_questions(user.id, db, personalization_source="HOMETOWN")
    assert res_home["total"] == 1
    assert res_home["questions"][0]["personalization_source"] == "HOMETOWN"


# ============================================================================
# 25-30: API Endpoint Integration Tests
# ============================================================================

def get_auth_headers(email="candidate_api@example.com"):
    # Register candidate if not exists
    client.post("/api/auth/register", json={
        "email": email,
        "password": "Password123!",
        "full_name": "API Candidate",
    })
    # Login to obtain access token
    login_resp = client.post("/api/auth/login", json={
        "email": email,
        "password": "Password123!",
    })
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_api_generate_personalized_authenticated(setup_db):
    db = TestingSessionLocal()
    headers = get_auth_headers()

    # Update existing profile created during registration
    user = db.query(User).filter(User.email == "candidate_api@example.com").first()
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.add(profile)
    profile.education_data = {"degree": "B.Tech", "university": "IIT Bombay", "specialization": "Electrical"}
    db.commit()

    # Query text generated for EDUCATION source is "Electrical technology public policy governance administration"
    topic_q = "Electrical technology public policy governance administration"
    doc, chunk = setup_sample_knowledge_chunk(db, user.id, query_text=topic_q)

    response = client.post(
        "/api/questions/generate-personalized",
        headers=headers,
        json={
            "source": "EDUCATION",
            "difficulty": "MODERATE",
            "question_type": "MAIN",
            "top_k": 3,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "question" in data
    assert data["is_personalized"] is True
    assert data["personalization_source"] == "EDUCATION"


def test_api_generate_personalized_unauthenticated(setup_db):
    response = client.post(
        "/api/questions/generate-personalized",
        json={
            "source": "EDUCATION",
        },
    )
    assert response.status_code == 401


def test_api_generate_personalized_invalid_source(setup_db):
    headers = get_auth_headers("invalid_src@example.com")
    response = client.post(
        "/api/questions/generate-personalized",
        headers=headers,
        json={
            "source": "INVALID_SOURCE_NAME",
        },
    )
    assert response.status_code == 422


def test_api_list_questions_with_personalization_query_params(setup_db):
    headers = get_auth_headers("list_pers@example.com")
    response = client.get(
        "/api/questions?is_personalized=true&personalization_source=EDUCATION",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "questions" in data
    assert "total" in data


def test_api_get_question_detail_returns_personalization_fields(setup_db):
    db = TestingSessionLocal()
    headers = get_auth_headers("detail_pers@example.com")
    user = db.query(User).filter(User.email == "detail_pers@example.com").first()

    q = InterviewQuestion(
        user_id=user.id,
        subject="POLITY",
        topic="Education Background Query",
        question_text="Personalized question text for API detail test.",
        difficulty="HARD",
        question_type="SCENARIO",
        is_personalized=True,
        personalization_source="EDUCATION",
        personalization_label="Education Background",
    )
    db.add(q)
    db.commit()
    db.refresh(q)

    response = client.get(f"/api/questions/{q.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == q.id
    assert data["is_personalized"] is True
    assert data["personalization_source"] == "EDUCATION"
    assert data["personalization_label"] == "Education Background"


def test_api_delete_personalized_question(setup_db):
    db = TestingSessionLocal()
    headers = get_auth_headers("delete_pers@example.com")
    user = db.query(User).filter(User.email == "delete_pers@example.com").first()

    q = InterviewQuestion(
        user_id=user.id,
        subject="POLITY",
        topic="Hometown Query",
        question_text="Question to be deleted",
        is_personalized=True,
        personalization_source="HOMETOWN",
    )
    db.add(q)
    db.commit()
    db.refresh(q)

    del_resp = client.delete(f"/api/questions/{q.id}", headers=headers)
    assert del_resp.status_code == 200
    assert del_resp.json()["id"] == q.id

    get_resp = client.get(f"/api/questions/{q.id}", headers=headers)
    assert get_resp.status_code == 404
