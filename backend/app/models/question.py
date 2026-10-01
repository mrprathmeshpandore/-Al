import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    current_affair_id = Column(String(36), ForeignKey("current_affairs.id", ondelete="SET NULL"), nullable=True, index=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False, default="MAIN", index=True)
    difficulty = Column(String(30), nullable=False, default="MODERATE", index=True)
    subject = Column(String(100), nullable=True, index=True)
    topic = Column(String(255), nullable=True, index=True)
    category = Column(String(100), nullable=True, index=True)

    # Phase 7 Personalization Fields
    is_personalized = Column(Boolean, default=False, nullable=False, index=True)
    personalization_source = Column(String(50), nullable=True, index=True)
    personalization_label = Column(String(255), nullable=True)

    explanation = Column(Text, nullable=True)
    why_this_matters = Column(Text, nullable=True)
    status = Column(String(30), nullable=False, default="ACTIVE", index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    sources = relationship("InterviewQuestionSource", back_populates="question", cascade="all, delete-orphan")
    current_affair = relationship("CurrentAffair", back_populates="questions")


class InterviewQuestionSource(Base):
    __tablename__ = "interview_question_sources"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question_id = Column(String(36), ForeignKey("interview_questions.id", ondelete="CASCADE"), nullable=False, index=True)
    resource_id = Column(String(36), nullable=True, index=True)
    document_id = Column(String(36), nullable=True, index=True)
    chunk_id = Column(String(36), nullable=True, index=True)
    resource_title = Column(String(255), nullable=False)
    page_number = Column(Integer, nullable=True)
    chunk_index = Column(Integer, nullable=True)
    similarity_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship
    question = relationship("InterviewQuestion", back_populates="sources")
