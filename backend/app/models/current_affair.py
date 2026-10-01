import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class CurrentAffair(Base):
    __tablename__ = "current_affairs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), nullable=False, unique=True, index=True)
    summary = Column(Text, nullable=True)
    source_name = Column(String(100), nullable=False, index=True)
    source_url = Column(String(1024), nullable=True, index=True)
    published_at = Column(DateTime, nullable=True, index=True)
    retrieved_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    category = Column(String(50), nullable=False, default="NATIONAL", index=True)
    topic = Column(String(100), nullable=True, index=True)
    subtopic = Column(String(100), nullable=True)
    content = Column(Text, nullable=True)
    key_points = Column(JSON, nullable=True)  # List[str]
    context = Column(Text, nullable=True)
    policy_response = Column(Text, nullable=True)
    upsc_relevance = Column(Text, nullable=True)
    interview_angle = Column(Text, nullable=True)
    analysis_status = Column(String(30), nullable=False, default="FETCHED", index=True)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    questions = relationship(
        "InterviewQuestion",
        back_populates="current_affair",
        cascade="all, delete-orphan",
    )
