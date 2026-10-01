import uuid
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class SessionStatus(str, Enum):
    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"


class InterviewType(str, Enum):
    FULL_INTERVIEW = "FULL_INTERVIEW"
    QUICK_PRACTICE = "QUICK_PRACTICE"
    DAF_INTERVIEW = "DAF_INTERVIEW"
    CURRENT_AFFAIRS = "CURRENT_AFFAIRS"
    CUSTOM = "CUSTOM"


class QuestionSessionStatus(str, Enum):
    PENDING = "PENDING"
    ASKED = "ASKED"
    ANSWERED = "ANSWERED"
    SKIPPED = "SKIPPED"


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(30), nullable=False, default=SessionStatus.CREATED.value, index=True)
    interview_type = Column(String(50), nullable=False, default=InterviewType.FULL_INTERVIEW.value, index=True)
    total_questions = Column(Integer, nullable=False, default=10)
    current_question_index = Column(Integer, nullable=False, default=1)
    include_adaptive = Column(Boolean, nullable=False, default=True)
    input_mode = Column(String(20), nullable=False, default="TEXT")
    language = Column(String(20), nullable=False, default="en-IN")
    
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user = relationship("User")
    session_questions = relationship(
        "InterviewSessionQuestion",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="InterviewSessionQuestion.sequence_number",
    )


class InterviewSessionQuestion(Base):
    __tablename__ = "interview_session_questions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(String(36), ForeignKey("interview_questions.id", ondelete="SET NULL"), nullable=True, index=True)
    sequence_number = Column(Integer, nullable=False)
    question_status = Column(String(30), nullable=False, default=QuestionSessionStatus.PENDING.value, index=True)

    # Adaptive Question Attributes (Phase 11)
    parent_session_question_id = Column(String(36), ForeignKey("interview_session_questions.id", ondelete="SET NULL"), nullable=True, index=True)
    parent_answer_id = Column(String(36), ForeignKey("interview_answers.id", ondelete="SET NULL"), nullable=True, index=True)
    question_depth = Column(Integer, nullable=False, default=0)
    generated_reason = Column(Text, nullable=True)
    adaptive_type = Column(String(30), nullable=False, default="MAIN", index=True)

    presented_at = Column(DateTime(timezone=True), nullable=True)
    answered_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    session = relationship("InterviewSession", back_populates="session_questions")
    question = relationship("InterviewQuestion")
    answers = relationship(
        "InterviewAnswer",
        foreign_keys="InterviewAnswer.session_question_id",
        back_populates="session_question",
        cascade="all, delete-orphan",
    )
    parent_session_question = relationship(
        "InterviewSessionQuestion",
        remote_side=[id],
        foreign_keys=[parent_session_question_id],
        backref="child_session_questions",
    )
    parent_answer = relationship("InterviewAnswer", foreign_keys=[parent_answer_id])


class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_question_id = Column(String(36), ForeignKey("interview_session_questions.id", ondelete="CASCADE"), nullable=False, index=True)
    answer_text = Column(Text, nullable=False)
    submitted_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    answer_duration_seconds = Column(Integer, nullable=False, default=0)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    session_question = relationship("InterviewSessionQuestion", foreign_keys=[session_question_id], back_populates="answers")
    evaluation = relationship("InterviewAnswerEvaluation", back_populates="answer", uselist=False, cascade="all, delete-orphan")
