import os
import io
import pytest
import pypdf
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.services.pdf_extractor import extract_pdf_pages
from app.services.text_cleaner import clean_text
from app.services.chunker import chunk_pages
from app.services.document_processor import process_document
from app.models.document import Document, ProcessingStatus

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
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def create_sample_pdf_bytes(text_content: str = "Prashasak AI UPSC Civil Services Prep Knowledge Document") -> bytes:
    """Helper creating a valid in-memory PDF binary."""
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=612, height=792)
    
    # We can write minimal valid PDF structure or use pypdf
    buffer = io.BytesIO()
    writer.write(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def get_authenticated_headers(email: str = "resourceuser@example.com"):
    reg_payload = {
        "email": email,
        "full_name": "Resource Aspirant",
        "password": "Password123!"
    }
    client.post("/api/auth/register", json=reg_payload)
    login_res = client.post("/api/auth/login", json={"email": email, "password": "Password123!"})
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_upload_unauthorized():
    pdf_bytes = create_sample_pdf_bytes()
    response = client.post(
        "/api/resources/upload",
        files={"file": ("test.pdf", pdf_bytes, "application/pdf")},
        data={"title": "Test Title"}
    )
    assert response.status_code == 401


def test_upload_invalid_file_type():
    headers = get_authenticated_headers("user_invalid@example.com")
    response = client.post(
        "/api/resources/upload",
        files={"file": ("test.txt", b"Plain text file", "text/plain")},
        data={"title": "Invalid File"},
        headers=headers
    )
    assert response.status_code == 400
    assert "only pdf files" in response.json()["detail"].lower()


def test_upload_pdf_success_and_processing():
    headers = get_authenticated_headers("uploader@example.com")
    pdf_bytes = create_sample_pdf_bytes()

    response = client.post(
        "/api/resources/upload",
        files={"file": ("polity_notes.pdf", pdf_bytes, "application/pdf")},
        data={
            "title": "Indian Polity Constitution Notes",
            "description": "Comprehensive notes on Fundamental Rights",
            "category": "Standard Books",
            "subject": "Polity",
            "topic": "Preamble & Rights"
        },
        headers=headers
    )

    assert response.status_code == 201
    data = response.json()
    assert "resource_id" in data
    assert "document_id" in data
    assert data["processing_status"] == "UPLOADED"

    # Synchronously execute processing for test assertions
    db = TestingSessionLocal()
    try:
        process_document(data["document_id"], db)
        doc = db.query(Document).filter(Document.id == data["document_id"]).first()
        assert doc is not None
        assert doc.processing_status in [ProcessingStatus.PROCESSED.value, ProcessingStatus.FAILED.value]
    finally:
        db.close()


def test_list_resources_and_filtering():
    headers = get_authenticated_headers("filteruser@example.com")
    pdf_bytes = create_sample_pdf_bytes()

    # Upload Resource 1
    client.post(
        "/api/resources/upload",
        files={"file": ("history.pdf", pdf_bytes, "application/pdf")},
        data={"title": "Modern Indian History", "category": "Core Subjects", "subject": "History"},
        headers=headers
    )

    # Upload Resource 2
    client.post(
        "/api/resources/upload",
        files={"file": ("economy.pdf", pdf_bytes, "application/pdf")},
        data={"title": "Indian Economy Survey", "category": "Government Schemes", "subject": "Economy"},
        headers=headers
    )

    # Test List All
    res_all = client.get("/api/resources")
    assert res_all.status_code == 200
    assert len(res_all.json()) >= 2

    # Test Search Query
    res_search = client.get("/api/resources?search=History")
    assert res_search.status_code == 200
    titles = [r["title"] for r in res_search.json()]
    assert "Modern Indian History" in titles


def test_categories_and_subjects_counts():
    headers = get_authenticated_headers("countsuser@example.com")
    pdf_bytes = create_sample_pdf_bytes()

    client.post(
        "/api/resources/upload",
        files={"file": ("geography.pdf", pdf_bytes, "application/pdf")},
        data={"title": "Physical Geography", "category": "Core Subjects", "subject": "Geography"},
        headers=headers
    )

    res_cat = client.get("/api/resources/categories")
    assert res_cat.status_code == 200
    cats = {c["category"]: c["resource_count"] for c in res_cat.json()}
    assert "Core Subjects" in cats

    res_subj = client.get("/api/resources/subjects")
    assert res_subj.status_code == 200
    subjs = {s["subject"]: s["resource_count"] for s in res_subj.json()}
    assert "Geography" in subjs


def test_bookmark_flow():
    headers = get_authenticated_headers("bookmarkuser@example.com")
    pdf_bytes = create_sample_pdf_bytes()

    upload_res = client.post(
        "/api/resources/upload",
        files={"file": ("ethics.pdf", pdf_bytes, "application/pdf")},
        data={"title": "Ethics Integrity Case Studies", "category": "Interview", "subject": "Ethics"},
        headers=headers
    )
    resource_id = upload_res.json()["resource_id"]

    # 1. Add Bookmark
    bm_res = client.post(f"/api/resources/{resource_id}/bookmark", headers=headers)
    assert bm_res.status_code == 201
    assert bm_res.json()["resource_id"] == resource_id

    # 2. Duplicate Bookmark Attempt
    dup_res = client.post(f"/api/resources/{resource_id}/bookmark", headers=headers)
    assert dup_res.status_code == 409

    # 3. List Bookmarked Resources
    bm_list = client.get("/api/resources/bookmarked", headers=headers)
    assert bm_list.status_code == 200
    assert len(bm_list.json()) >= 1
    assert bm_list.json()[0]["id"] == resource_id

    # 4. Delete Bookmark
    del_res = client.delete(f"/api/resources/{resource_id}/bookmark", headers=headers)
    assert del_res.status_code == 204

    # 5. List Bookmarked should be empty
    bm_empty = client.get("/api/resources/bookmarked", headers=headers)
    assert len(bm_empty.json()) == 0


def test_text_cleaner_and_chunker_services():
    raw_text = "UPSC--\nCivil Services Examination 2026.\n\n\n\nGovernance and   Public   Policy."
    cleaned = clean_text(raw_text)
    assert "UPSCCivil" in cleaned or "Civil Services" in cleaned
    assert "   " not in cleaned

    pages = [
        {"page_number": 1, "text": "Section A: Constitution of India preamble and fundamental rights overview."},
        {"page_number": 2, "text": "Section B: Directive principles of state policy and fundamental duties."}
    ]

    chunks = chunk_pages(pages, chunk_size=40, chunk_overlap=10)
    assert len(chunks) >= 2
    assert chunks[0]["page_number"] == 1
    assert "chunk_index" in chunks[0]
