import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.user import User
from app.models.profile import UserProfile
from app.utils.security import hash_password, verify_password

# Test database using in-memory SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_user_creation_and_password_security():
    db = TestingSessionLocal()
    hashed_pwd = hash_password("Secret123!")
    user = User(
        email="aspirant@prashasak.ai",
        full_name="Pratham Aspirant",
        password_hash=hashed_pwd
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    assert user.id is not None
    assert user.email == "aspirant@prashasak.ai"
    assert verify_password("Secret123!", user.password_hash)
    assert not verify_password("WrongPassword", user.password_hash)
    db.close()


def test_user_profile_relationship():
    db = TestingSessionLocal()
    hashed_pwd = hash_password("Password123")
    user = User(
        email="profile_test@prashasak.ai",
        full_name="Test User",
        password_hash=hashed_pwd
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    profile = UserProfile(
        user_id=user.id,
        home_state="Maharashtra",
        district="Pune",
        current_city="Pune",
        gender="Male",
        profile_completion=85
    )
    db.add(profile)
    db.commit()

    fetched_user = db.query(User).filter(User.id == user.id).first()
    assert fetched_user.profile is not None
    assert fetched_user.profile.home_state == "Maharashtra"
    assert fetched_user.profile.profile_completion == 85
    db.close()
