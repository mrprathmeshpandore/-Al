import io
import pytest
import pypdf
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.config import settings
from app.core.database import Base, get_db
from app.models.user import User
from app.models.document import Document, ProcessingStatus
from app.models.document_chunk import DocumentChunk, EmbeddingStatus
from app.models.question import InterviewQuestion, InterviewQuestionSource
from app.services.embedding_provider import FakeEmbeddingProvider
from app.services.gemini_service import FakeGeminiService
from app.services.question_generation_service import generate_interview_question, UNGROUNDED_QUESTION_MESSAGE
from app.services.embedding_service import compute_content_hash

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


def create_sample_pdf_bytes() -> bytes:
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=612, height=792)
    buffer = io.BytesIO()
    writer.write(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def get_authenticated_headers(email: str = "q_user@example.com"):
    reg_payload = {
        "email": email,
        "full_name": "Questions Aspirant",
        "password": "Password123!"
    }
    client.post("/api/auth/register", json=reg_payload)
    login_res = client.post("/api/auth/login", json={"email": email, "password": "Password123!"})
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def setup_user_and_chunk(email: str, topic: str, content: str):
    headers = get_authenticated_headers(email)
    pdf_bytes = create_sample_pdf_bytes()

    upload_res = client.post(
        "/api/resources/upload",
        files={"file": ("polity_notes.pdf", pdf_bytes, "application/pdf")},
        data={"title": "Indian Polity & Governance", "subject": "Polity", "category": "Core"},
        headers=headers
    )
    doc_id = upload_res.json()["document_id"]

    db = TestingSessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        provider = FakeEmbeddingProvider(vector_dim=768)
        vec = provider.embed_text(topic)

        chunk = DocumentChunk(
            document_id=doc_id,
            chunk_index=0,
            page_number=42,
            content=content,
            content_hash=compute_content_hash(content),
            embedding=vec,
            embedding_status=EmbeddingStatus.COMPLETED.value
        )
        db.add(chunk)
        doc = db.query(Document).filter(Document.id == doc_id).first()
        doc.processing_status = ProcessingStatus.PROCESSED.value
        db.commit()
        return headers, user.id, doc_id
    finally:
        db.close()


# 1. Test Successful MAIN Question Generation
def test_successful_main_question_generation():
    headers, user_id, doc_id = setup_user_and_chunk(
        "main_q@example.com",
        "Fundamental Rights",
        "Article 14 guarantees equality before law and equal protection of laws within territory of India."
    )

    mock_gemini = FakeGeminiService(
        mock_answer="How does Article 14 ensure constitutional morality in public administration?",
        mock_grounded=True,
        mock_source_indexes=[1]
    )

    db = TestingSessionLocal()
    try:
        provider = FakeEmbeddingProvider(vector_dim=768)
        res_data = generate_interview_question(
            topic="Fundamental Rights",
            current_user_id=user_id,
            db=db,
            subject="Polity",
            question_type="MAIN",
            difficulty="MODERATE",
            gemini_service=mock_gemini,
            embedding_provider=provider
        )

        assert res_data["id"] is not None
        assert res_data["question_type"] == "MAIN"
        assert res_data["difficulty"] == "MODERATE"
        assert res_data["grounded"] is True
        assert len(res_data["sources"]) == 1
        assert res_data["sources"][0]["resource_title"] == "Indian Polity & Governance"
    finally:
        db.close()


# 2. Test Successful FOLLOW_UP Generation
def test_successful_followup_question_generation():
    headers, user_id, doc_id = setup_user_and_chunk(
        "followup_q@example.com",
        "Directive Principles",
        "DPSP under Part IV guide the State in policy formulation for welfare state."
    )

    mock_gemini = FakeGeminiService(
        mock_answer="If DPSPs are non-justiciable, how can an administrator balance them with justiciable rights?",
        mock_grounded=True,
        mock_source_indexes=[1]
    )

    db = TestingSessionLocal()
    try:
        provider = FakeEmbeddingProvider(vector_dim=768)
        res_data = generate_interview_question(
            topic="Directive Principles",
            current_user_id=user_id,
            db=db,
            question_type="FOLLOW_UP",
            gemini_service=mock_gemini,
            embedding_provider=provider
        )
        assert res_data["question_type"] == "FOLLOW_UP"
    finally:
        db.close()


# 3. Test Successful COUNTER Question Generation
def test_successful_counter_question_generation():
    headers, user_id, doc_id = setup_user_and_chunk(
        "counter_q@example.com",
        "Federalism",
        "Indian federalism is quasi-federal with strong central bias during emergencies."
    )

    mock_gemini = FakeGeminiService(
        mock_answer="You argue for strong states, but how would you address regional disparities without central intervention?",
        mock_grounded=True
    )

    db = TestingSessionLocal()
    try:
        provider = FakeEmbeddingProvider(vector_dim=768)
        res_data = generate_interview_question(
            topic="Federalism",
            current_user_id=user_id,
            db=db,
            question_type="COUNTER",
            gemini_service=mock_gemini,
            embedding_provider=provider
        )
        assert res_data["question_type"] == "COUNTER"
    finally:
        db.close()


# 4. Test Successful ETHICAL Generation
def test_successful_ethical_question_generation():
    headers, user_id, doc_id = setup_user_and_chunk(
        "ethical_q@example.com",
        "Civil Service Ethics",
        "Integrity and public interest must guide administrative discretionary powers."
    )

    mock_gemini = FakeGeminiService(
        mock_answer="When political pressure conflicts with ethical duty, what decision matrix would you follow as District Magistrate?",
        mock_grounded=True
    )

    db = TestingSessionLocal()
    try:
        provider = FakeEmbeddingProvider(vector_dim=768)
        res_data = generate_interview_question(
            topic="Civil Service Ethics",
            current_user_id=user_id,
            db=db,
            question_type="ETHICAL",
            gemini_service=mock_gemini,
            embedding_provider=provider
        )
        assert res_data["question_type"] == "ETHICAL"
    finally:
        db.close()


# 5. Test Successful SCENARIO Generation
def test_successful_scenario_question_generation():
    headers, user_id, doc_id = setup_user_and_chunk(
        "scenario_q@example.com",
        "Disaster Management",
        "NDRF coordinates rescue operations during cyclone alerts in coastal districts."
    )

    mock_gemini = FakeGeminiService(
        mock_answer="You are District Collector facing imminent flooding and local resistance to evacuation. How do you resolve this?",
        mock_grounded=True
    )

    db = TestingSessionLocal()
    try:
        provider = FakeEmbeddingProvider(vector_dim=768)
        res_data = generate_interview_question(
            topic="Disaster Management",
            current_user_id=user_id,
            db=db,
            question_type="SCENARIO",
            gemini_service=mock_gemini,
            embedding_provider=provider
        )
        assert res_data["question_type"] == "SCENARIO"
    finally:
        db.close()


# 6. Test Difficulty Handling
def test_difficulty_handling():
    headers, user_id, doc_id = setup_user_and_chunk(
        "diff_q@example.com",
        "Judicial Review",
        "Judicial review maintains constitutional supremacy under Article 13 and 32."
    )

    mock_gemini = FakeGeminiService(
        mock_answer="Examine the delicate balance between judicial activism and judicial overreach in India.",
        mock_grounded=True
    )

    db = TestingSessionLocal()
    try:
        provider = FakeEmbeddingProvider(vector_dim=768)
        res_data = generate_interview_question(
            topic="Judicial Review",
            current_user_id=user_id,
            db=db,
            difficulty="HARD",
            gemini_service=mock_gemini,
            embedding_provider=provider
        )
        assert res_data["difficulty"] == "HARD"
    finally:
        db.close()


# 7. Test RAG Retrieval Integration
def test_rag_retrieval_integration():
    headers, user_id, doc_id = setup_user_and_chunk(
        "rag_q@example.com",
        "Preamble Principles",
        "The Preamble declares India to be a Sovereign Socialist Secular Democratic Republic."
    )

    res = client.post(
        "/api/questions/generate",
        json={"topic": "Preamble Principles", "question_type": "MAIN"},
        headers=headers
    )
    assert res.status_code == 201
    data = res.json()
    assert data["grounded"] is True
    assert len(data["sources"]) > 0


# 8. Test Context Passed to Gemini
def test_context_passed_to_gemini():
    headers, user_id, doc_id = setup_user_and_chunk(
        "context_q@example.com",
        "Panchayati Raj",
        "73rd Amendment Act 1992 constitutionalized Panchayati Raj Institutions."
    )

    mock_gemini = MagicMock()
    mock_gemini.generate_grounded_answer.return_value = {
        "answer": "How does 73rd Amendment empower rural local self-governance?",
        "why_this_matters": "Local governance relevance",
        "explanation": "Panchayat empowerment analysis",
        "grounded": True,
        "source_indexes": [1]
    }

    db = TestingSessionLocal()
    try:
        provider = FakeEmbeddingProvider(vector_dim=768)
        generate_interview_question(
            topic="Panchayati Raj",
            current_user_id=user_id,
            db=db,
            gemini_service=mock_gemini,
            embedding_provider=provider
        )

        mock_gemini.generate_grounded_answer.assert_called_once()
        prompt_arg = mock_gemini.generate_grounded_answer.call_args[1]["prompt"]
        assert "73rd Amendment Act" in prompt_arg
    finally:
        db.close()


# 9. Test Empty Retrieval Safe Fallback
def test_empty_retrieval_safe_fallback():
    db = TestingSessionLocal()
    try:
        provider = FakeEmbeddingProvider(vector_dim=768)
        mock_gemini = MagicMock()

        res_data = generate_interview_question(
            topic="Nonexistent Topic in Empty Database",
            current_user_id="empty_user_id",
            db=db,
            gemini_service=mock_gemini,
            embedding_provider=provider
        )

        assert res_data["grounded"] is False
        assert res_data["message"] == UNGROUNDED_QUESTION_MESSAGE
        assert res_data["sources"] == []
        mock_gemini.generate_grounded_answer.assert_not_called()
    finally:
        db.close()


# 10. Test Similarity Threshold Enforcement
def test_similarity_threshold_enforcement():
    db = TestingSessionLocal()
    try:
        provider = FakeEmbeddingProvider(vector_dim=768)
        mock_gemini = MagicMock()

        res_data = generate_interview_question(
            topic="Unmatched query string below threshold",
            current_user_id="threshold_user_id",
            db=db,
            gemini_service=mock_gemini,
            embedding_provider=provider
        )

        assert res_data["grounded"] is False
        assert res_data["sources"] == []
        mock_gemini.generate_grounded_answer.assert_not_called()
    finally:
        db.close()


# 11. Test Gemini Failure Handling
def test_gemini_failure_handling():
    headers, user_id, doc_id = setup_user_and_chunk(
        "fail_q@example.com",
        "Public Accounts Committee",
        "PAC examines audit report of CAG to enforce parliamentary control over finances."
    )

    failing_gemini = FakeGeminiService(should_fail=True)

    db = TestingSessionLocal()
    try:
        provider = FakeEmbeddingProvider(vector_dim=768)
        res_data = generate_interview_question(
            topic="Public Accounts Committee",
            current_user_id=user_id,
            db=db,
            gemini_service=failing_gemini,
            embedding_provider=provider
        )

        assert res_data["grounded"] is False
        assert res_data["sources"] == []
    finally:
        db.close()


# 12. Test Malformed Gemini JSON
def test_malformed_gemini_json():
    headers, user_id, doc_id = setup_user_and_chunk(
        "malform_q@example.com",
        "Electoral Reforms",
        "Model Code of Conduct guides political parties during elections."
    )

    malformed_gemini = FakeGeminiService(should_malform=True)

    db = TestingSessionLocal()
    try:
        provider = FakeEmbeddingProvider(vector_dim=768)
        res_data = generate_interview_question(
            topic="Electoral Reforms",
            current_user_id=user_id,
            db=db,
            gemini_service=malformed_gemini,
            embedding_provider=provider
        )

        assert res_data["grounded"] is False
        assert res_data["sources"] == []
    finally:
        db.close()


# 13. Test Invalid Request Validation
def test_invalid_request_validation():
    headers = get_authenticated_headers("val_req@example.com")

    # Empty topic
    res1 = client.post("/api/questions/generate", json={"topic": ""}, headers=headers)
    assert res1.status_code == 422

    # Invalid question type
    res2 = client.post("/api/questions/generate", json={"topic": "Valid", "question_type": "INVALID_TYPE"}, headers=headers)
    assert res2.status_code == 422

    # Invalid difficulty
    res3 = client.post("/api/questions/generate", json={"topic": "Valid", "difficulty": "SUPER_HARD"}, headers=headers)
    assert res3.status_code == 422


# 14. Test Duplicate Question Detection
def test_duplicate_question_detection():
    headers, user_id, doc_id = setup_user_and_chunk(
        "dup_q@example.com",
        "Separation of Powers",
        "Separation of powers divides governance functions between Legislature, Executive, and Judiciary."
    )

    mock_gemini = FakeGeminiService(
        mock_answer="Explain the doctrine of separation of powers in Indian governance system.",
        mock_grounded=True
    )

    db = TestingSessionLocal()
    try:
        provider = FakeEmbeddingProvider(vector_dim=768)

        # First generation
        res1 = generate_interview_question(
            topic="Separation of Powers",
            current_user_id=user_id,
            db=db,
            gemini_service=mock_gemini,
            embedding_provider=provider
        )
        id1 = res1["id"]

        # Second generation with identical question text
        res2 = generate_interview_question(
            topic="Separation of Powers",
            current_user_id=user_id,
            db=db,
            gemini_service=mock_gemini,
            embedding_provider=provider
        )

        assert res2["id"] == id1
        # Assert database contains only 1 question record
        count = db.query(InterviewQuestion).filter(InterviewQuestion.user_id == user_id).count()
        assert count == 1
    finally:
        db.close()


# 15. Test Backend Citation Mapping
def test_backend_citation_mapping():
    headers, user_id, doc_id = setup_user_and_chunk(
        "cit_map@example.com",
        "Cabinet Secretariat",
        "Cabinet Secretariat ensures inter-ministerial coordination in central government."
    )

    mock_gemini = FakeGeminiService(
        mock_answer="What is the role of Cabinet Secretary as head of civil service?",
        mock_grounded=True,
        mock_source_indexes=[1]
    )

    db = TestingSessionLocal()
    try:
        provider = FakeEmbeddingProvider(vector_dim=768)
        res_data = generate_interview_question(
            topic="Cabinet Secretariat",
            current_user_id=user_id,
            db=db,
            gemini_service=mock_gemini,
            embedding_provider=provider
        )

        assert len(res_data["sources"]) == 1
        source = res_data["sources"][0]
        assert source["resource_title"] == "Indian Polity & Governance"
        assert source["page_number"] == 42
    finally:
        db.close()


# 16. Test Model-Generated Citation Metadata Ignored
def test_model_generated_citation_metadata_ignored():
    headers, user_id, doc_id = setup_user_and_chunk(
        "ignore_cit@example.com",
        "Governor Powers",
        "Article 163 defines discretionary powers of the Governor."
    )

    # Gemini output text claims fake source metadata, but backend uses real retrieved chunk
    mock_gemini = FakeGeminiService(
        mock_answer="Analyze constitutional role of Governor under Article 163. Source: Fake Book Page 99",
        mock_grounded=True,
        mock_source_indexes=[1]
    )

    db = TestingSessionLocal()
    try:
        provider = FakeEmbeddingProvider(vector_dim=768)
        res_data = generate_interview_question(
            topic="Governor Powers",
            current_user_id=user_id,
            db=db,
            gemini_service=mock_gemini,
            embedding_provider=provider
        )

        assert res_data["sources"][0]["resource_title"] == "Indian Polity & Governance"
        assert res_data["sources"][0]["page_number"] == 42
    finally:
        db.close()


# 17. Test User Question Isolation
def test_user_question_isolation():
    headers_a, user_id_a, doc_a = setup_user_and_chunk("user_a_iso@example.com", "Topic A", "Content A for User A")
    headers_b = get_authenticated_headers("user_b_iso@example.com")

    # User A generates a question
    res_a = client.post(
        "/api/questions/generate",
        json={"topic": "Topic A"},
        headers=headers_a
    )
    assert res_a.status_code == 201
    q_id_a = res_a.json()["id"]

    # User B attempts to access User A's question
    res_b = client.get(f"/api/questions/{q_id_a}", headers=headers_b)
    assert res_b.status_code == 404


# 18. Test User Source Isolation
def test_user_source_isolation():
    headers_a, user_id_a, doc_a = setup_user_and_chunk("src_user_a@example.com", "Confidential Strategy A", "User A Private Notes")
    headers_b = get_authenticated_headers("src_user_b@example.com")

    # User B tries to generate a question on User A's confidential topic
    res_b = client.post(
        "/api/questions/generate",
        json={"topic": "Confidential Strategy A"},
        headers=headers_b
    )
    assert res_b.status_code == 201
    assert res_b.json()["grounded"] is False
    assert res_b.json()["sources"] == []


# 19. Test Unauthorized Access Blocked
def test_unauthorized_access_blocked():
    res1 = client.post("/api/questions/generate", json={"topic": "Test"})
    assert res1.status_code == 401

    res2 = client.get("/api/questions")
    assert res2.status_code == 401

    res3 = client.get("/api/questions/dummy-id")
    assert res3.status_code == 401


# 20. Test Pagination
def test_pagination():
    headers = get_authenticated_headers("page_user@example.com")
    db = TestingSessionLocal()
    try:
        user = db.query(User).filter(User.email == "page_user@example.com").first()
        for i in range(15):
            q = InterviewQuestion(
                user_id=user.id,
                question_text=f"Question text {i+1} for pagination testing?",
                question_type="MAIN",
                difficulty="MODERATE",
                subject="Polity",
                topic=f"Topic {i+1}",
                why_this_matters="Relevance context",
                status="ACTIVE"
            )
            db.add(q)
        db.commit()

        # Page 1
        res1 = client.get("/api/questions?page=1&page_size=10", headers=headers)
        assert res1.status_code == 200
        data1 = res1.json()
        assert data1["total"] == 15
        assert len(data1["questions"]) == 10
        assert data1["page"] == 1

        # Page 2
        res2 = client.get("/api/questions?page=2&page_size=10", headers=headers)
        assert res2.status_code == 200
        data2 = res2.json()
        assert len(data2["questions"]) == 5
        assert data2["page"] == 2
    finally:
        db.close()


# 21. Test Filtering by Subject
def test_filtering_by_subject():
    headers = get_authenticated_headers("filt_sub@example.com")
    db = TestingSessionLocal()
    try:
        user = db.query(User).filter(User.email == "filt_sub@example.com").first()
        db.add(InterviewQuestion(user_id=user.id, question_text="Polity Question?", subject="Polity", status="ACTIVE"))
        db.add(InterviewQuestion(user_id=user.id, question_text="History Question?", subject="History", status="ACTIVE"))
        db.commit()

        res = client.get("/api/questions?subject=Polity", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 1
        assert data["questions"][0]["subject"] == "Polity"
    finally:
        db.close()


# 22. Test Filtering by Difficulty
def test_filtering_by_difficulty():
    headers = get_authenticated_headers("filt_diff@example.com")
    db = TestingSessionLocal()
    try:
        user = db.query(User).filter(User.email == "filt_diff@example.com").first()
        db.add(InterviewQuestion(user_id=user.id, question_text="Easy Q?", difficulty="EASY", status="ACTIVE"))
        db.add(InterviewQuestion(user_id=user.id, question_text="Hard Q?", difficulty="HARD", status="ACTIVE"))
        db.commit()

        res = client.get("/api/questions?difficulty=HARD", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 1
        assert data["questions"][0]["difficulty"] == "HARD"
    finally:
        db.close()


# 23. Test Filtering by Question Type
def test_filtering_by_question_type():
    headers = get_authenticated_headers("filt_type@example.com")
    db = TestingSessionLocal()
    try:
        user = db.query(User).filter(User.email == "filt_type@example.com").first()
        db.add(InterviewQuestion(user_id=user.id, question_text="Main Q?", question_type="MAIN", status="ACTIVE"))
        db.add(InterviewQuestion(user_id=user.id, question_text="Ethical Q?", question_type="ETHICAL", status="ACTIVE"))
        db.commit()

        res = client.get("/api/questions?question_type=ETHICAL", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 1
        assert data["questions"][0]["question_type"] == "ETHICAL"
    finally:
        db.close()


# 24. Test Question Detail Endpoint
def test_question_detail_endpoint():
    headers, user_id, doc_id = setup_user_and_chunk(
        "detail_q@example.com",
        "Public Administration",
        "Public administration enforces law and executes administrative policy."
    )

    gen_res = client.post(
        "/api/questions/generate",
        json={"topic": "Public Administration"},
        headers=headers
    )
    assert gen_res.status_code == 201
    q_id = gen_res.json()["id"]

    detail_res = client.get(f"/api/questions/{q_id}", headers=headers)
    assert detail_res.status_code == 200
    data = detail_res.json()
    assert data["id"] == q_id
    assert data["topic"] == "Public Administration"
    assert len(data["sources"]) > 0


# 25. Test Question Persistence
def test_question_persistence():
    headers, user_id, doc_id = setup_user_and_chunk(
        "persist_q@example.com",
        "Constitutional Morality",
        "Constitutional morality entails adherence to core constitutional values."
    )

    gen_res = client.post(
        "/api/questions/generate",
        json={"topic": "Constitutional Morality"},
        headers=headers
    )
    assert gen_res.status_code == 201
    q_id = gen_res.json()["id"]

    db = TestingSessionLocal()
    try:
        q_db = db.query(InterviewQuestion).filter(InterviewQuestion.id == q_id).first()
        assert q_db is not None
        assert q_db.user_id == user_id
        assert q_db.topic == "Constitutional Morality"
    finally:
        db.close()


# 26. Test Source Relation Persistence
def test_source_relation_persistence():
    headers, user_id, doc_id = setup_user_and_chunk(
        "persist_src@example.com",
        "Finance Commission",
        "Article 280 provides for Finance Commission for vertical and horizontal tax devolution."
    )

    gen_res = client.post(
        "/api/questions/generate",
        json={"topic": "Finance Commission"},
        headers=headers
    )
    assert gen_res.status_code == 201
    q_id = gen_res.json()["id"]

    db = TestingSessionLocal()
    try:
        q_db = db.query(InterviewQuestion).filter(InterviewQuestion.id == q_id).first()
        assert len(q_db.sources) > 0
        src = q_db.sources[0]
        assert src.resource_title == "Indian Polity & Governance"
        assert src.page_number == 42
    finally:
        db.close()
