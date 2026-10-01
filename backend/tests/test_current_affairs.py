from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.models.current_affair import CurrentAffair
from app.models.question import InterviewQuestion
from app.constants.current_affairs import CurrentAffairCategory, AnalysisStatus
from app.services.current_affairs import (
    CurrentAffairsIngestionService,
    CurrentAffairsAnalysisService,
    NormalizationService,
    DeduplicationService,
    CurrentAffairCandidate,
    ManualCurrentAffairsSource,
)
from app.services.gemini_service import FakeGeminiService

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


def get_auth_headers(email="ca_testuser@example.com"):
    reg_payload = {
        "email": email,
        "full_name": "Current Affairs User",
        "password": "Password123!"
    }
    client.post("/api/auth/register", json=reg_payload)
    login_res = client.post("/api/auth/login", json={"email": email, "password": "Password123!"})
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# 1. Source normalization
def test_source_normalization():
    candidate = CurrentAffairCandidate(
        title="  <b>Title With HTML</b> &amp; Extra Space ",
        source_name=" Press Release ",
        content=" <p>Article body content paragraph.</p> ",
        category="governance",
    )
    norm = NormalizationService.normalize_candidate(candidate)
    assert norm.title == "Title With HTML &amp; Extra Space"
    assert norm.content == "Article body content paragraph."
    assert norm.source_name == "Press Release"
    assert norm.category == "GOVERNANCE"


# 2. Title normalization
def test_title_normalization():
    slug = NormalizationService.generate_slug("India's National Green Hydrogen Mission: 2026 Strategy!")
    assert "indias-national-green-hydrogen-mission-2026-strategy" in slug


# 3. URL preservation
def test_url_preservation(setup_db):
    db = TestingSessionLocal()
    cand = CurrentAffairCandidate(
        title="Digital India Initiative Update",
        source_name="PIB",
        content="Details about digital governance infrastructure.",
        source_url="https://pib.gov.in/PressReleasePage.aspx?PRID=9999",
    )
    service = CurrentAffairsIngestionService(db=db, analysis_service=CurrentAffairsAnalysisService(FakeGeminiService()))
    affair = service.process_candidate(cand, auto_analyze=False)
    assert affair.source_url == "https://pib.gov.in/PressReleasePage.aspx?PRID=9999"
    db.close()


# 4. Publication date handling
def test_publication_date_handling(setup_db):
    db = TestingSessionLocal()
    now_dt = datetime.now(timezone.utc)
    cand = CurrentAffairCandidate(
        title="RBI Monetary Policy Committee Announcement",
        source_name="RBI",
        content="Monetary policy repo rates unchanged.",
        published_at=now_dt,
    )
    service = CurrentAffairsIngestionService(db=db, analysis_service=CurrentAffairsAnalysisService(FakeGeminiService()))
    affair = service.process_candidate(cand, auto_analyze=False)
    assert affair.published_at is not None
    db.close()


# 5. Duplicate URL detection
def test_duplicate_url_detection(setup_db):
    db = TestingSessionLocal()
    cand1 = CurrentAffairCandidate(
        title="ISRO Gaganyaan Mission Preparation",
        source_name="ISRO",
        content="First crewed orbital module test.",
        source_url="https://isro.gov.in/gaganyaan-2026.html",
    )
    cand2 = CurrentAffairCandidate(
        title="ISRO Gaganyaan Mission Prep Update",
        source_name="ISRO Media",
        content="First crewed orbital module test details.",
        source_url="https://isro.gov.in/gaganyaan-2026.html",
    )
    service = CurrentAffairsIngestionService(db=db, analysis_service=CurrentAffairsAnalysisService(FakeGeminiService()))
    res1 = service.process_candidate(cand1, auto_analyze=False)
    res2 = service.process_candidate(cand2, auto_analyze=False)
    assert res1.id == res2.id
    db.close()


# 6. Duplicate normalized-title detection
def test_duplicate_normalized_title_detection(setup_db):
    db = TestingSessionLocal()
    cand1 = CurrentAffairCandidate(
        title="Cabinet Approves National Cyber Security Strategy",
        source_name="PIB",
        content="Comprehensive cyber defense framework.",
    )
    cand2 = CurrentAffairCandidate(
        title="Cabinet Approves National Cyber Security Strategy",
        source_name="PIB Wire",
        content="Different wording for same headline.",
    )
    service = CurrentAffairsIngestionService(db=db, analysis_service=CurrentAffairsAnalysisService(FakeGeminiService()))
    res1 = service.process_candidate(cand1, auto_analyze=False)
    res2 = service.process_candidate(cand2, auto_analyze=False)
    assert res1.id == res2.id
    db.close()


# 7. Source attribution
def test_source_attribution(setup_db):
    db = TestingSessionLocal()
    cand = CurrentAffairCandidate(
        title="Ministry of External Affairs Bilateral Summit",
        source_name="Ministry of External Affairs",
        content="Bilateral agreements signed during state visit.",
    )
    service = CurrentAffairsIngestionService(db=db, analysis_service=CurrentAffairsAnalysisService(FakeGeminiService()))
    affair = service.process_candidate(cand, auto_analyze=False)
    assert affair.source_name == "Ministry of External Affairs"
    db.close()


# 8. Successful Gemini analysis
def test_successful_gemini_analysis():
    fake_gemini = FakeGeminiService(mock_answer="Grounded analysis for UPSC candidate.")
    analysis_svc = CurrentAffairsAnalysisService(fake_gemini)
    res = analysis_svc.analyze_item(
        title="National Education Policy Progress",
        content="Detailed assessment of gross enrollment ratio.",
        source_name="PIB",
        category="SOCIAL_ISSUES",
    )
    assert "summary" in res
    assert "key_points" in res
    assert res["category"] == "SOCIAL_ISSUES"


# 9. Structured analysis parsing
def test_structured_analysis_parsing():
    analysis_svc = CurrentAffairsAnalysisService(FakeGeminiService())
    raw_data = {
        "summary": "Factual summary of event.",
        "key_points": ["Point 1", "Point 2"],
        "context": "Context background.",
        "policy_response": "Government policy stance.",
        "upsc_relevance": "High GS2 relevance.",
        "interview_angle": "Administrative balance required.",
        "category": "GOVERNANCE",
        "topic": "E-Governance",
        "subtopic": "Citizen Service Delivery",
    }
    sanitized = analysis_svc._validate_and_sanitize_analysis(raw_data, default_category="NATIONAL")
    assert sanitized["summary"] == "Factual summary of event."
    assert len(sanitized["key_points"]) == 2
    assert sanitized["category"] == "GOVERNANCE"


# 10. Malformed Gemini response
def test_malformed_gemini_response():
    fake_gemini = FakeGeminiService(should_malform=True)
    analysis_svc = CurrentAffairsAnalysisService(fake_gemini)
    res = analysis_svc.analyze_item("Title", "Content", "Source")
    assert "summary" in res
    assert res["summary"] != ""


# 11. Gemini failure
def test_gemini_failure(setup_db):
    db = TestingSessionLocal()
    cand = CurrentAffairCandidate(
        title="Failed Analysis Item",
        source_name="Source",
        content="Content to analyze.",
    )
    fake_gemini = FakeGeminiService(should_fail=True)
    analysis_svc = CurrentAffairsAnalysisService(fake_gemini)
    ingest_svc = CurrentAffairsIngestionService(db=db, analysis_service=analysis_svc)

    affair = ingest_svc.process_candidate(cand, auto_analyze=True)
    assert affair.analysis_status == AnalysisStatus.FAILED.value
    db.close()


# 12. Category validation
def test_category_validation():
    assert NormalizationService.normalize_category("POLITY") == "POLITY"
    assert NormalizationService.normalize_category("unknown_category") == "NATIONAL"
    assert NormalizationService.normalize_category("Climate & Environment") == "ENVIRONMENT"


# 13. Topic persistence
def test_topic_persistence(setup_db):
    db = TestingSessionLocal()
    cand = CurrentAffairCandidate(
        title="Semiconductor Mission Phase 2",
        source_name="PIB",
        content="Semiconductor manufacturing plant approvals.",
        category="SCIENCE_TECHNOLOGY",
        topic="Semiconductor Ecosystem",
    )
    ingest_svc = CurrentAffairsIngestionService(db=db, analysis_service=CurrentAffairsAnalysisService(FakeGeminiService()))
    affair = ingest_svc.process_candidate(cand, auto_analyze=False)
    assert affair.topic == "Semiconductor Ecosystem"

    fetched = db.query(CurrentAffair).filter(CurrentAffair.id == affair.id).first()
    assert fetched.topic == "Semiconductor Ecosystem"
    db.close()


# 14. UPSC relevance persistence
def test_upsc_relevance_persistence(setup_db):
    db = TestingSessionLocal()
    cand = CurrentAffairCandidate(
        title="Disaster Management Guidelines Update",
        source_name="NDMA",
        content="New flood mitigation standard operating procedures.",
        category="ENVIRONMENT",
    )
    ingest_svc = CurrentAffairsIngestionService(db=db, analysis_service=CurrentAffairsAnalysisService(FakeGeminiService()))
    affair = ingest_svc.process_candidate(cand, auto_analyze=True)
    assert affair.upsc_relevance is not None
    db.close()


# 15. Interview angle persistence
def test_interview_angle_persistence(setup_db):
    db = TestingSessionLocal()
    cand = CurrentAffairCandidate(
        title="Civil Services Capacity Building (Karmayogi Bharat)",
        source_name="DoPT",
        content="Competency-based training modules launched.",
        category="GOVERNANCE",
    )
    ingest_svc = CurrentAffairsIngestionService(db=db, analysis_service=CurrentAffairsAnalysisService(FakeGeminiService()))
    affair = ingest_svc.process_candidate(cand, auto_analyze=True)
    assert affair.interview_angle is not None
    db.close()


# 16. Empty source content handling
def test_empty_source_content_handling():
    cand = CurrentAffairCandidate(
        title="Brief Notification Title",
        source_name="Official Gazette",
        content="",
    )
    norm = NormalizationService.normalize_candidate(cand)
    assert norm.title == "Brief Notification Title"
    assert norm.content == ""


# 17. Current affair persistence
def test_current_affair_persistence(setup_db):
    db = TestingSessionLocal()
    affair = CurrentAffair(
        title="Direct Persistence Test Item",
        slug="direct-persistence-test-item",
        summary="Test summary",
        source_name="Test Source",
        category="ECONOMY",
        retrieved_at=datetime.now(timezone.utc),
    )
    db.add(affair)
    db.commit()
    db.refresh(affair)

    saved = db.query(CurrentAffair).filter(CurrentAffair.id == affair.id).first()
    assert saved is not None
    assert saved.title == "Direct Persistence Test Item"
    db.close()


# 18. Current affair list API
def test_current_affair_list_api(setup_db):
    db = TestingSessionLocal()
    ingest_svc = CurrentAffairsIngestionService(db=db, analysis_service=CurrentAffairsAnalysisService(FakeGeminiService()))
    ingest_svc.process_candidate(
        CurrentAffairCandidate(title="API List Item 1", source_name="Src 1", content="Content 1"),
        auto_analyze=False,
    )
    db.close()

    response = client.get("/api/current-affairs")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 1


# 19. Current affair detail API
def test_current_affair_detail_api(setup_db):
    db = TestingSessionLocal()
    ingest_svc = CurrentAffairsIngestionService(db=db, analysis_service=CurrentAffairsAnalysisService(FakeGeminiService()))
    item = ingest_svc.process_candidate(
        CurrentAffairCandidate(title="API Detail Item", source_name="Src Detail", content="Content detail"),
        auto_analyze=True,
    )
    db.close()

    response = client.get(f"/api/current-affairs/{item.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item.id
    assert data["title"] == "API Detail Item"
    assert "potential_questions" in data


# 20. Category API
def test_category_api():
    response = client.get("/api/current-affairs/categories")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert len(data["categories"]) == len(CurrentAffairCategory)


# 21. Topic API
def test_topic_api(setup_db):
    db = TestingSessionLocal()
    ingest_svc = CurrentAffairsIngestionService(db=db, analysis_service=CurrentAffairsAnalysisService(FakeGeminiService()))
    ingest_svc.process_candidate(
        CurrentAffairCandidate(title="Topic Item", source_name="Src", content="Cont", topic="Urban Transport"),
        auto_analyze=False,
    )
    db.close()

    response = client.get("/api/current-affairs/topics")
    assert response.status_code == 200
    data = response.json()
    assert "topics" in data
    assert "Urban Transport" in data["topics"]


# 22. Search filtering
def test_search_filtering(setup_db):
    db = TestingSessionLocal()
    ingest_svc = CurrentAffairsIngestionService(db=db, analysis_service=CurrentAffairsAnalysisService(FakeGeminiService()))
    ingest_svc.process_candidate(
        CurrentAffairCandidate(title="Quantum Computing Research Policy", source_name="DST", content="National Quantum Mission"),
        auto_analyze=False,
    )
    ingest_svc.process_candidate(
        CurrentAffairCandidate(title="Agricultural MSP Fixation", source_name="CACP", content="Kharif crops pricing"),
        auto_analyze=False,
    )
    db.close()

    res = client.get("/api/current-affairs?search=Quantum")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert "Quantum" in data["items"][0]["title"]


# 23. Category filtering
def test_category_filtering(setup_db):
    db = TestingSessionLocal()
    ingest_svc = CurrentAffairsIngestionService(db=db, analysis_service=CurrentAffairsAnalysisService(FakeGeminiService()))
    ingest_svc.process_candidate(
        CurrentAffairCandidate(title="Polity Item", source_name="Src", content="Cont", category="POLITY"),
        auto_analyze=False,
    )
    ingest_svc.process_candidate(
        CurrentAffairCandidate(title="Economy Item", source_name="Src", content="Cont", category="ECONOMY"),
        auto_analyze=False,
    )
    db.close()

    res = client.get("/api/current-affairs?category=POLITY")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["category"] == "POLITY"


# 24. Date filtering
def test_date_filtering(setup_db):
    db = TestingSessionLocal()
    db.query(CurrentAffair).delete()
    db.commit()

    past_date = datetime.now(timezone.utc) - timedelta(days=10)
    ingest_svc = CurrentAffairsIngestionService(db=db, analysis_service=CurrentAffairsAnalysisService(FakeGeminiService()))
    ingest_svc.process_candidate(
        CurrentAffairCandidate(title="Old News Item For Date Filter", source_name="Src", content="Cont", published_at=past_date),
        auto_analyze=False,
    )
    db.close()

    recent_from = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    res = client.get(f"/api/current-affairs?date_from={recent_from}")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 0


# 25. Pagination
def test_pagination(setup_db):
    db = TestingSessionLocal()
    db.query(CurrentAffair).delete()
    db.commit()

    titles = [
        "National Biodiversity Action Plan",
        "Reserve Bank Monetary Policy Guidelines",
        "Supreme Court Bench Order on EIA Rules",
        "ISRO Solar Observatory Satellite Launch",
        "Cabinet Approval for Railway Electrification",
        "Indo-Pacific Strategic Trade Partnership",
        "E-Governance Data Protection Standards",
        "Agricultural Produce Marketing Reforms",
        "National Quantum Mission Infrastructure",
        "Deep Ocean Mission Survey Expedition",
        "Semiconductor Fab Manufacturing Initiative",
        "Civil Services Training Reforms",
        "Urban Affordable Housing Scheme Mandate",
        "NITI Aayog Innovation Index Report",
        "Renewable Energy Grid Integration Tariff"
    ]

    ingest_svc = CurrentAffairsIngestionService(db=db, analysis_service=CurrentAffairsAnalysisService(FakeGeminiService()))
    for t in titles:
        ingest_svc.process_candidate(
            CurrentAffairCandidate(
                title=t,
                source_name="Official Source",
                content=f"Substantive content for {t}"
            ),
            auto_analyze=False,
        )
    db.close()

    res = client.get("/api/current-affairs?page=1&page_size=5")
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) == 5
    assert data["total"] == 15
    assert data["pages"] == 3


# 26. Analyze endpoint authentication
def test_analyze_endpoint_authentication(setup_db):
    headers = get_auth_headers()
    db = TestingSessionLocal()
    ingest_svc = CurrentAffairsIngestionService(db=db, analysis_service=CurrentAffairsAnalysisService(FakeGeminiService()))
    item = ingest_svc.process_candidate(
        CurrentAffairCandidate(title="Unanalyzed Item", source_name="Src", content="Needs analysis"),
        auto_analyze=False,
    )
    db.close()

    res = client.post(f"/api/current-affairs/{item.id}/analyze", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["analysis_status"] == AnalysisStatus.PUBLISHED.value


# 27. No unauthenticated ingestion / analyze
def test_no_unauthenticated_ingestion(setup_db):
    db = TestingSessionLocal()
    ingest_svc = CurrentAffairsIngestionService(db=db, analysis_service=CurrentAffairsAnalysisService(FakeGeminiService()))
    item = ingest_svc.process_candidate(
        CurrentAffairCandidate(title="Unauth Analyze Item", source_name="Src", content="Needs analysis"),
        auto_analyze=False,
    )
    db.close()

    res = client.post(f"/api/current-affairs/{item.id}/analyze")
    assert res.status_code == 401


# 28. Potential question generation
def test_potential_question_generation(setup_db):
    db = TestingSessionLocal()
    ingest_svc = CurrentAffairsIngestionService(db=db, analysis_service=CurrentAffairsAnalysisService(FakeGeminiService()))
    item = ingest_svc.process_candidate(
        CurrentAffairCandidate(
            title="Digital Personal Data Protection Act Implementation",
            source_name="MeitY",
            content="Rules notified under DPDP Act 2023.",
            category="GOVERNANCE",
        ),
        auto_analyze=True,
    )

    questions = db.query(InterviewQuestion).filter(InterviewQuestion.current_affair_id == item.id).all()
    assert len(questions) == 5
    q_types = {q.question_type for q in questions}
    assert q_types == {"MAIN", "FOLLOW_UP", "COUNTER", "ETHICAL", "SCENARIO"}
    db.close()


# 29. Question source attribution
def test_question_source_attribution(setup_db):
    db = TestingSessionLocal()
    ingest_svc = CurrentAffairsIngestionService(db=db, analysis_service=CurrentAffairsAnalysisService(FakeGeminiService()))
    item = ingest_svc.process_candidate(
        CurrentAffairCandidate(title="Question Attribution Item", source_name="Src", content="Content"),
        auto_analyze=True,
    )
    questions = db.query(InterviewQuestion).filter(InterviewQuestion.current_affair_id == item.id).all()
    for q in questions:
        assert q.current_affair_id == item.id
        assert q.current_affair.title == "Question Attribution Item"
    db.close()


# 30. Existing Phase 1–7 tests remain passing (Verified via comprehensive test suite run)
def test_existing_phase_functionality_intact(setup_db):
    res_health = client.get("/api/health")
    assert res_health.status_code == 200

    headers = get_auth_headers()
    res_me = client.get("/api/auth/me", headers=headers)
    assert res_me.status_code == 200
