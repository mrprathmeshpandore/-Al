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


def test_register_success():
    payload = {
        "email": "testaspirant@example.com",
        "full_name": "Test Aspirant",
        "password": "SecurePassword123!"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testaspirant@example.com"
    assert data["full_name"] == "Test Aspirant"
    assert data["is_active"] is True
    assert "password" not in data
    assert "password_hash" not in data


def test_register_duplicate_email():
    payload = {
        "email": "duplicate@example.com",
        "full_name": "First Aspirant",
        "password": "Password123!"
    }
    res1 = client.post("/api/auth/register", json=payload)
    assert res1.status_code == 201

    # Attempt registration with same email
    res2 = client.post("/api/auth/register", json=payload)
    assert res2.status_code == 409
    assert "already registered" in res2.json()["detail"].lower()


def test_register_invalid_password():
    payload = {
        "email": "shortpwd@example.com",
        "full_name": "Short Pwd User",
        "password": "123"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 422


def test_login_success():
    reg_payload = {
        "email": "logintest@example.com",
        "full_name": "Login User",
        "password": "MySecretPassword123!"
    }
    client.post("/api/auth/register", json=reg_payload)

    login_payload = {
        "email": "logintest@example.com",
        "password": "MySecretPassword123!"
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "logintest@example.com"


def test_login_invalid_credentials():
    login_payload = {
        "email": "nonexistent@example.com",
        "password": "WrongPassword!"
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 401
    assert "invalid email or password" in response.json()["detail"].lower()


def test_get_me_authorized():
    reg_payload = {
        "email": "me@example.com",
        "full_name": "Me Aspirant",
        "password": "Password123!"
    }
    client.post("/api/auth/register", json=reg_payload)

    login_res = client.post("/api/auth/login", json={"email": "me@example.com", "password": "Password123!"})
    token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    assert data["full_name"] == "Me Aspirant"


def test_get_me_unauthorized():
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_google_login_mock(monkeypatch):
    # Mock Google Token Verification
    mock_data = {
        "email": "googleuser@example.com",
        "name": "Google Aspirant",
        "sub": "google-123456789"
    }
    monkeypatch.setattr("google.oauth2.id_token.verify_oauth2_token", lambda token, req, audience: mock_data)

    response = client.post("/api/auth/google", json={"credential": "mock_google_id_token_xyz"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "googleuser@example.com"
    assert data["user"]["full_name"] == "Google Aspirant"
