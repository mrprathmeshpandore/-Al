import io
import pytest
import pypdf
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.config import settings
from app.core.database import Base, get_db
from app.models.document import Document, ProcessingStatus
from app.models.document_chunk import DocumentChunk, EmbeddingStatus
from app.services.embedding_provider import FakeEmbeddingProvider
from app.services.embedding_service import process_chunk_embeddings, compute_content_hash
from app.services.document_processor import process_document
from app.services.retrieval_service import search_knowledge_base, compute_cosine_similarity
from app.scripts.reindex_documents import reindex_all_documents

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


def get_authenticated_headers(email: str = "raguser@example.com"):
    reg_payload = {
        "email": email,
        "full_name": "RAG Aspirant",
        "password": "Password123!"
    }
    client.post("/api/auth/register", json=reg_payload)
    login_res = client.post("/api/auth/login", json={"email": email, "password": "Password123!"})
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_fake_embedding_provider_dimensions():
    provider = FakeEmbeddingProvider(vector_dim=768)
    vec = provider.embed_text("Indian Constitution Article 370")
    assert len(vec) == 768
    # Test magnitude ~ 1.0
    magnitude = sum(x * x for x in vec) ** 0.5
    assert abs(magnitude - 1.0) < 0.01


def test_batch_embedding_service():
    chunks = [
        {"chunk_index": 0, "page_number": 1, "content": "Article 14 guarantees equality before law."},
        {"chunk_index": 1, "page_number": 1, "content": "Article 21 protects protection of life and personal liberty."}
    ]
    provider = FakeEmbeddingProvider(vector_dim=768)
    res = process_chunk_embeddings(chunks, provider=provider)

    assert len(res) == 2
    assert res[0]["content_hash"] == compute_content_hash(chunks[0]["content"])
    assert res[0]["embedding_status"] == EmbeddingStatus.COMPLETED.value
    assert len(res[0]["embedding"]) == 768


def test_cosine_similarity_math():
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    v3 = [0.0, 1.0, 0.0]
    assert compute_cosine_similarity(v1, v2) == 1.0
    assert compute_cosine_similarity(v1, v3) == 0.0


def test_rag_search_api_flow_and_citation_metadata():
    headers = get_authenticated_headers("rag_search_user@example.com")
    pdf_bytes = create_sample_pdf_bytes()

    # Upload PDF
    upload_res = client.post(
        "/api/resources/upload",
        files={"file": ("polity.pdf", pdf_bytes, "application/pdf")},
        data={
            "title": "Indian Polity & Governance Handbook",
            "category": "Core Subjects",
            "subject": "Polity",
            "topic": "Federal System"
        },
        headers=headers
    )
    assert upload_res.status_code == 201
    doc_id = upload_res.json()["document_id"]
    res_id = upload_res.json()["resource_id"]

    # Insert a dummy processed chunk into DB manually for deterministic vector matching
    db = TestingSessionLocal()
    try:
        provider = FakeEmbeddingProvider(vector_dim=768)
        query_text = "What is the role of Federalism in Indian Polity?"
        query_vec = provider.embed_text(query_text)

        chunk = DocumentChunk(
            document_id=doc_id,
            chunk_index=0,
            page_number=42,
            content="Federalism in India is a basic structure of the Constitution as held in SR Bommai case.",
            content_hash=compute_content_hash("Federalism in India..."),
            chunk_metadata={"word_count": 14},
            embedding=query_vec,  # Exact match vector for test assertion
            embedding_status=EmbeddingStatus.COMPLETED.value
        )
        db.add(chunk)

        doc = db.query(Document).filter(Document.id == doc_id).first()
        doc.processing_status = ProcessingStatus.PROCESSED.value
        db.commit()
    finally:
        db.close()

    # Test POST /api/rag/search
    search_payload = {
        "query": "What is the role of Federalism in Indian Polity?",
        "top_k": 3,
        "filters": {"subject": "Polity"}
    }
    search_res = client.post("/api/rag/search", json=search_payload, headers=headers)
    assert search_res.status_code == 200
    data = search_res.json()

    assert data["query"] == search_payload["query"]
    assert len(data["results"]) >= 1

    item = data["results"][0]
    assert item["resource_title"] == "Indian Polity & Governance Handbook"
    assert item["page_number"] == 42
    assert item["chunk_index"] == 0
    assert item["subject"] == "Polity"
    assert item["score"] > 0.9
    assert "embedding" not in item  # Verify raw vector is NOT exposed in response


def test_rag_similarity_threshold_filtering():
    headers = get_authenticated_headers("threshold_user@example.com")
    db = TestingSessionLocal()
    try:
        # Perform search with non-matching query where no vectors meet RAG_MIN_SIMILARITY
        res = search_knowledge_base(
            query="Quantum Computing Particle Physics Algorithms",
            top_k=5,
            filters={},
            current_user_id="threshold_user",
            db=db,
            provider=FakeEmbeddingProvider(vector_dim=768)
        )
        assert res["results"] == []
        assert "No sufficiently relevant content" in res["message"]
    finally:
        db.close()


def test_user_isolation_rag_search():
    headers_a = get_authenticated_headers("usera_rag@example.com")
    headers_b = get_authenticated_headers("userb_rag@example.com")
    pdf_bytes = create_sample_pdf_bytes()

    # User A uploads a private resource
    up_a = client.post(
        "/api/resources/upload",
        files={"file": ("private_notes_a.pdf", pdf_bytes, "application/pdf")},
        data={"title": "User A Private Notes", "category": "Personal", "subject": "History"},
        headers=headers_a
    )
    doc_id_a = up_a.json()["document_id"]

    db = TestingSessionLocal()
    try:
        provider = FakeEmbeddingProvider(vector_dim=768)
        vec_a = provider.embed_text("Confidential User A Secret Data")
        chunk_a = DocumentChunk(
            document_id=doc_id_a,
            chunk_index=0,
            page_number=1,
            content="Confidential User A Secret Data",
            embedding=vec_a,
            embedding_status=EmbeddingStatus.COMPLETED.value
        )
        db.add(chunk_a)
        doc_a = db.query(Document).filter(Document.id == doc_id_a).first()
        doc_a.processing_status = ProcessingStatus.PROCESSED.value
        db.commit()

        # User B searches for User A's secret query
        search_res_b = client.post(
            "/api/rag/search",
            json={"query": "Confidential User A Secret Data"},
            headers=headers_b
        )
        assert search_res_b.status_code == 200
        assert len(search_res_b.json()["results"]) == 0
    finally:
        db.close()


def test_reindex_script_execution():
    db = TestingSessionLocal()
    try:
        result = reindex_all_documents(force=False, db=db)
        assert "success" in result
        assert "failed" in result
    finally:
        db.close()
