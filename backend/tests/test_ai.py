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
from app.services.embedding_provider import FakeEmbeddingProvider
from app.services.gemini_service import FakeGeminiService, BaseGeminiService
from app.services.rag_answer_service import generate_rag_grounded_answer, SAFE_UNGROUNDED_ANSWER
from app.services.context_builder import build_rag_context
from app.services.citation_service import build_backend_citations
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


def get_authenticated_headers(email: str = "ai_user@example.com"):
    reg_payload = {
        "email": email,
        "full_name": "UPSC Candidate",
        "password": "Password123!"
    }
    client.post("/api/auth/register", json=reg_payload)
    login_res = client.post("/api/auth/login", json={"email": email, "password": "Password123!"})
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# 1. Test Successful Grounded Answer
def test_successful_grounded_answer():
    headers = get_authenticated_headers("user_grounded@example.com")
    pdf_bytes = create_sample_pdf_bytes()

    upload_res = client.post(
        "/api/resources/upload",
        files={"file": ("polity.pdf", pdf_bytes, "application/pdf")},
        data={"title": "Indian Constitution Notes", "subject": "Polity", "category": "Core"},
        headers=headers
    )
    doc_id = upload_res.json()["document_id"]

    db = TestingSessionLocal()
    try:
        provider = FakeEmbeddingProvider(vector_dim=768)
        query = "What is Article 21 of the Indian Constitution?"
        vec = provider.embed_text(query)

        chunk = DocumentChunk(
            document_id=doc_id,
            chunk_index=0,
            page_number=15,
            content="Article 21 provides that no person shall be deprived of his life or personal liberty except according to procedure established by law.",
            content_hash=compute_content_hash("Article 21..."),
            embedding=vec,
            embedding_status=EmbeddingStatus.COMPLETED.value
        )
        db.add(chunk)
        doc = db.query(Document).filter(Document.id == doc_id).first()
        doc.processing_status = ProcessingStatus.PROCESSED.value
        db.commit()

        # Patch Gemini service with mock answer
        mock_gemini = FakeGeminiService(
            mock_answer="Article 21 guarantees Protection of Life and Personal Liberty under the Constitution.",
            mock_grounded=True,
            mock_source_indexes=[1]
        )

        user = db.query(User).filter(User.email == "user_grounded@example.com").first()

        res_data = generate_rag_grounded_answer(
            query=query,
            current_user_id=user.id,
            db=db,
            gemini_service=mock_gemini,
            embedding_provider=provider
        )

        assert res_data["query"] == query
        assert res_data["grounded"] is True
        assert "Protection of Life" in res_data["answer"]
        assert len(res_data["sources"]) == 1
        assert res_data["sources"][0]["resource_title"] == "Indian Constitution Notes"
        assert res_data["sources"][0]["page_number"] == 15
        assert res_data["sources"][0]["chunk_index"] == 0
    finally:
        db.close()


# 2. Test RAG Retrieval Integration via API
def test_rag_retrieval_integration():
    headers = get_authenticated_headers("user_retrieval@example.com")
    pdf_bytes = create_sample_pdf_bytes()

    upload_res = client.post(
        "/api/resources/upload",
        files={"file": ("history.pdf", pdf_bytes, "application/pdf")},
        data={"title": "Modern History Summary", "subject": "History", "category": "General"},
        headers=headers
    )
    doc_id = upload_res.json()["document_id"]

    db = TestingSessionLocal()
    try:
        provider = FakeEmbeddingProvider(vector_dim=768)
        query = "Discuss the Non-Cooperation Movement of 1920."
        vec = provider.embed_text(query)

        chunk = DocumentChunk(
            document_id=doc_id,
            chunk_index=2,
            page_number=8,
            content="The Non-Cooperation Movement was launched by Mahatma Gandhi in 1920 to resist British rule in India.",
            embedding=vec,
            embedding_status=EmbeddingStatus.COMPLETED.value
        )
        db.add(chunk)
        doc = db.query(Document).filter(Document.id == doc_id).first()
        doc.processing_status = ProcessingStatus.PROCESSED.value
        db.commit()

        # Invoke POST /api/ai/ask via API client
        res = client.post(
            "/api/ai/ask",
            json={"query": query, "top_k": 3},
            headers=headers
        )
        assert res.status_code == 200
        data = res.json()
        assert data["query"] == query
        assert data["grounded"] is True
        assert len(data["sources"]) > 0
    finally:
        db.close()


# 3. Test Correct Citation Metadata
def test_correct_citation_metadata():
    chunks = [
        {
            "resource_id": "res_123",
            "resource_title": "Governance in India",
            "document_id": "doc_456",
            "page_number": 42,
            "chunk_index": 3,
            "score": 0.9421
        }
    ]
    citations = build_backend_citations(chunks)
    assert len(citations) == 1
    c = citations[0]
    assert c["resource_id"] == "res_123"
    assert c["resource_title"] == "Governance in India"
    assert c["document_id"] == "doc_456"
    assert c["page_number"] == 42
    assert c["chunk_index"] == 3
    assert c["score"] == 0.9421


# 4. Test Empty Retrieval Returns Safe Response
def test_empty_retrieval_returns_safe_response():
    db = TestingSessionLocal()
    try:
        provider = FakeEmbeddingProvider(vector_dim=768)
        mock_gemini = MagicMock()

        res_data = generate_rag_grounded_answer(
            query="Unrelated topic with zero DB records",
            current_user_id="empty_user",
            db=db,
            gemini_service=mock_gemini,
            embedding_provider=provider
        )

        assert res_data["grounded"] is False
        assert res_data["answer"] == SAFE_UNGROUNDED_ANSWER
        assert res_data["sources"] == []
        # Assert Gemini was NOT called when retrieval is empty
        mock_gemini.generate_grounded_answer.assert_not_called()
    finally:
        db.close()


# 5. Test Similarity Threshold Behavior
def test_similarity_threshold_behavior():
    db = TestingSessionLocal()
    try:
        provider = FakeEmbeddingProvider(vector_dim=768)
        mock_gemini = MagicMock()

        # Query that produces low similarity below RAG_MIN_SIMILARITY
        res_data = generate_rag_grounded_answer(
            query="Random string query with low score",
            current_user_id="threshold_user",
            db=db,
            gemini_service=mock_gemini,
            embedding_provider=provider
        )

        assert res_data["grounded"] is False
        assert res_data["sources"] == []
        mock_gemini.generate_grounded_answer.assert_not_called()
    finally:
        db.close()


# 6. Test Gemini API Failure Handling
def test_gemini_api_failure_handling():
    headers = get_authenticated_headers("user_fail@example.com")
    pdf_bytes = create_sample_pdf_bytes()

    upload_res = client.post(
        "/api/resources/upload",
        files={"file": ("notes.pdf", pdf_bytes, "application/pdf")},
        data={"title": "Economics Notes", "subject": "Economy"},
        headers=headers
    )
    doc_id = upload_res.json()["document_id"]

    db = TestingSessionLocal()
    try:
        provider = FakeEmbeddingProvider(vector_dim=768)
        query = "What is Repo Rate?"
        vec = provider.embed_text(query)

        chunk = DocumentChunk(
            document_id=doc_id,
            chunk_index=0,
            page_number=1,
            content="Repo rate is the key interest rate at which RBI lends short term money to commercial banks.",
            embedding=vec,
            embedding_status=EmbeddingStatus.COMPLETED.value
        )
        db.add(chunk)
        doc = db.query(Document).filter(Document.id == doc_id).first()
        doc.processing_status = ProcessingStatus.PROCESSED.value
        db.commit()

        # Mock Gemini service throwing 500 error
        failing_gemini = FakeGeminiService(should_fail=True)

        res_data = generate_rag_grounded_answer(
            query=query,
            current_user_id="user_fail@example.com",
            db=db,
            gemini_service=failing_gemini,
            embedding_provider=provider
        )

        assert res_data["grounded"] is False
        assert res_data["answer"] == SAFE_UNGROUNDED_ANSWER
        assert res_data["sources"] == []
    finally:
        db.close()


# 7. Test Gemini Timeout Handling
def test_gemini_timeout_handling():
    db = TestingSessionLocal()
    try:
        provider = FakeEmbeddingProvider(vector_dim=768)
        timeout_gemini = FakeGeminiService(should_timeout=True)

        res_data = generate_rag_grounded_answer(
            query="Test timeout question",
            current_user_id="user_timeout@example.com",
            db=db,
            gemini_service=timeout_gemini,
            embedding_provider=provider
        )

        assert res_data["grounded"] is False
        assert res_data["answer"] == SAFE_UNGROUNDED_ANSWER
        assert res_data["sources"] == []
    finally:
        db.close()


# 8. Test Gemini Malformed Response
def test_gemini_malformed_response():
    db = TestingSessionLocal()
    try:
        provider = FakeEmbeddingProvider(vector_dim=768)
        malformed_gemini = FakeGeminiService(should_malform=True)

        res_data = generate_rag_grounded_answer(
            query="Test malformed question",
            current_user_id="user_malformed@example.com",
            db=db,
            gemini_service=malformed_gemini,
            embedding_provider=provider
        )

        assert res_data["grounded"] is False
        assert res_data["sources"] == []
    finally:
        db.close()


# 9. Test Invalid Query Validation
def test_invalid_query_validation():
    headers = get_authenticated_headers("val_user@example.com")

    # Empty string query
    res1 = client.post("/api/ai/ask", json={"query": ""}, headers=headers)
    assert res1.status_code == 422

    # Whitespace only query
    res2 = client.post("/api/ai/ask", json={"query": "   "}, headers=headers)
    assert res2.status_code == 422


# 10. Test top_k Boundary Validation
def test_top_k_boundary_validation():
    headers = get_authenticated_headers("topk_user@example.com")

    # top_k = 0 (below min boundary 1)
    res1 = client.post("/api/ai/ask", json={"query": "Valid Query", "top_k": 0}, headers=headers)
    assert res1.status_code == 422

    # top_k = 50 (above max boundary 20)
    res2 = client.post("/api/ai/ask", json={"query": "Valid Query", "top_k": 50}, headers=headers)
    assert res2.status_code == 422


# 11. Test User Resource Isolation in AI Ask
def test_user_resource_isolation_in_ai_ask():
    headers_a = get_authenticated_headers("user_iso_a@example.com")
    headers_b = get_authenticated_headers("user_iso_b@example.com")
    pdf_bytes = create_sample_pdf_bytes()

    # User A uploads a private document
    up_a = client.post(
        "/api/resources/upload",
        files={"file": ("secret.pdf", pdf_bytes, "application/pdf")},
        data={"title": "User A Top Secret Strategy", "subject": "Polity"},
        headers=headers_a
    )
    doc_id_a = up_a.json()["document_id"]

    db = TestingSessionLocal()
    try:
        provider = FakeEmbeddingProvider(vector_dim=768)
        secret_query = "What is User A Top Secret Strategy?"
        vec_a = provider.embed_text(secret_query)

        chunk_a = DocumentChunk(
            document_id=doc_id_a,
            chunk_index=0,
            page_number=1,
            content="User A Secret Strategy is strict privacy.",
            embedding=vec_a,
            embedding_status=EmbeddingStatus.COMPLETED.value
        )
        db.add(chunk_a)
        doc_a = db.query(Document).filter(Document.id == doc_id_a).first()
        doc_a.processing_status = ProcessingStatus.PROCESSED.value
        db.commit()

        # User B asks for User A's secret query
        res_b = client.post(
            "/api/ai/ask",
            json={"query": secret_query},
            headers=headers_b
        )
        assert res_b.status_code == 200
        data_b = res_b.json()

        # User B gets safe fallback with grounded=False and zero sources from User A
        assert data_b["grounded"] is False
        assert data_b["sources"] == []
    finally:
        db.close()


# 12. Test No Gemini Call When Retrieval Is Empty
def test_no_gemini_call_when_retrieval_is_empty():
    db = TestingSessionLocal()
    try:
        provider = FakeEmbeddingProvider(vector_dim=768)
        mock_gemini = MagicMock()

        res = generate_rag_grounded_answer(
            query="Empty DB query test",
            current_user_id="user_empty_call",
            db=db,
            gemini_service=mock_gemini,
            embedding_provider=provider
        )

        assert res["grounded"] is False
        assert res["sources"] == []
        assert mock_gemini.generate_grounded_answer.call_count == 0
    finally:
        db.close()


# 13. Test Model-Generated Citation Metadata Ignored
def test_model_generated_citation_metadata_ignored():
    chunks = [
        {
            "resource_id": "real_res_1",
            "resource_title": "Real Resource Title",
            "document_id": "real_doc_1",
            "page_number": 10,
            "chunk_index": 0,
            "score": 0.95
        }
    ]

    # Even if Gemini returns hallucinated text claiming Page 99 in title "Fake Title", backend citations strictly use chunks
    citations = build_backend_citations(chunks, referenced_source_indexes=[1])
    assert len(citations) == 1
    assert citations[0]["resource_title"] == "Real Resource Title"
    assert citations[0]["page_number"] == 10


# 14. Test Backend Generated Citation Metadata Preserved
def test_backend_generated_citation_metadata_preserved():
    retrieved = [
        {"resource_id": "r1", "resource_title": "Title 1", "document_id": "d1", "page_number": 5, "chunk_index": 1, "score": 0.88},
        {"resource_id": "r2", "resource_title": "Title 2", "document_id": "d2", "page_number": 12, "chunk_index": 0, "score": 0.77}
    ]
    citations = build_backend_citations(retrieved)
    assert len(citations) == 2
    assert citations[0]["resource_id"] == "r1"
    assert citations[1]["resource_id"] == "r2"


# 15. Test Grounded=False Behavior
def test_grounded_false_behavior():
    db = TestingSessionLocal()
    try:
        provider = FakeEmbeddingProvider(vector_dim=768)
        ungrounded_gemini = FakeGeminiService(
            mock_answer="I could not find sufficient information in context.",
            mock_grounded=False,
            mock_source_indexes=[]
        )

        res_data = generate_rag_grounded_answer(
            query="Query with context that turns out insufficient",
            current_user_id="user_ungrounded",
            db=db,
            gemini_service=ungrounded_gemini,
            embedding_provider=provider
        )

        assert res_data["grounded"] is False
        assert res_data["sources"] == []
    finally:
        db.close()


# 16. Test Streaming API Endpoint /api/ai/ask/stream
def test_ai_ask_stream_endpoint():
    headers = get_authenticated_headers("user_stream@example.com")
    pdf_bytes = create_sample_pdf_bytes()

    upload_res = client.post(
        "/api/resources/upload",
        files={"file": ("stream_doc.pdf", pdf_bytes, "application/pdf")},
        data={"title": "Stream Doc Notes", "subject": "Polity"},
        headers=headers
    )
    doc_id = upload_res.json()["document_id"]

    db = TestingSessionLocal()
    try:
        provider = FakeEmbeddingProvider(vector_dim=768)
        query = "What is the Preamble?"
        vec = provider.embed_text(query)

        chunk = DocumentChunk(
            document_id=doc_id,
            chunk_index=0,
            page_number=1,
            content="The Preamble to the Constitution of India is a brief introductory statement.",
            embedding=vec,
            embedding_status=EmbeddingStatus.COMPLETED.value
        )
        db.add(chunk)
        doc = db.query(Document).filter(Document.id == doc_id).first()
        doc.processing_status = ProcessingStatus.PROCESSED.value
        db.commit()

        # Invoke POST /api/ai/ask/stream
        res = client.post(
            "/api/ai/ask/stream",
            json={"query": query, "top_k": 3},
            headers=headers
        )
        assert res.status_code == 200
        assert "text/event-stream" in res.headers["content-type"]
        assert "event: metadata" in res.text
        assert "event: token" in res.text
    finally:
        db.close()

