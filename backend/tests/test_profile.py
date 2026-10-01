import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db

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


def get_authenticated_headers(email: str = "profileuser@example.com", name: str = "Profile Aspirant"):
    reg_payload = {
        "email": email,
        "full_name": name,
        "password": "Password123!"
    }
    client.post("/api/auth/register", json=reg_payload)
    login_res = client.post("/api/auth/login", json={"email": email, "password": "Password123!"})
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_get_profile_unauthorized():
    response = client.get("/api/profile")
    assert response.status_code == 401


def test_get_profile_authenticated():
    headers = get_authenticated_headers("user1@example.com", "Aspirant One")
    response = client.get("/api/profile", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "profile" in data
    assert "completion_percentage" in data
    assert data["profile"]["personal"]["fullName"] == "Aspirant One"


def test_update_profile_and_completion_calculation():
    headers = get_authenticated_headers("dafuser@example.com", "DAF Aspirant")

    update_payload = {
        "personal": {
            "fullName": "DAF Aspirant Updated",
            "dob": "1998-05-15",
            "homeState": "Maharashtra",
            "district": "Pune",
            "currentCity": "Pune",
            "gender": "Male"
        },
        "education": {
            "degree": "B.Tech",
            "university": "COEP Pune",
            "specialization": "Computer Engineering"
        },
        "upscJourney": {
            "attemptCount": "2nd Attempt",
            "optionalSubject": "Public Administration",
            "preparationStage": "Interview Ready"
        },
        "interests": {
            "hobbies": "Trekking, Chess, Reading Modern History"
        },
        "perspective": {
            "whyCivilServices": "To serve grassroot governance and contribute to public policy execution."
        }
    }

    response = client.put("/api/profile", json=update_payload, headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert data["profile"]["personal"]["homeState"] == "Maharashtra"
    assert data["profile"]["education"]["degree"] == "B.Tech"
    assert data["profile"]["upscJourney"]["optionalSubject"] == "Public Administration"
    assert data["completion_percentage"] == 100


def test_user_isolation_profile_access():
    headers_user_a = get_authenticated_headers("usera@example.com", "User A")
    headers_user_b = get_authenticated_headers("userb@example.com", "User B")

    client.put("/api/profile", json={
        "personal": {"fullName": "User A", "homeState": "Gujarat", "dob": "1995-01-01", "district": "Surat", "currentCity": "Surat", "gender": "Male"}
    }, headers=headers_user_a)

    res_b = client.get("/api/profile", headers=headers_user_b)
    assert res_b.status_code == 200
    profile_b = res_b.json()["profile"]

    assert profile_b["personal"]["fullName"] == "User B"
    assert profile_b["personal"]["homeState"] == ""
