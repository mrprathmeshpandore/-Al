import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    # Personal Information
    date_of_birth = Column(String(50), nullable=True)
    home_state = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    current_city = Column(String(100), nullable=True)
    gender = Column(String(20), nullable=True)

    # Structured DAF Modules (JSON/JSONB compatibility)
    education_data = Column(JSON, nullable=True)
    upsc_journey_data = Column(JSON, nullable=True)
    interests = Column(JSON, nullable=True)
    perspective = Column(JSON, nullable=True)

    profile_completion = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship back to User
    user = relationship("User", back_populates="profile")
