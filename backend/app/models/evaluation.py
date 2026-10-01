import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class InterviewAnswerEvaluation(Base):
    __tablename__ = "interview_answer_evaluations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    answer_id = Column(
        String(36),
        ForeignKey("interview_answers.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Dimension Scores & Feedbacks
    content_score = Column(Float, nullable=False)
    content_feedback = Column(Text, nullable=False)

    clarity_score = Column(Float, nullable=False)
    clarity_feedback = Column(Text, nullable=False)

    depth_score = Column(Float, nullable=False)
    depth_feedback = Column(Text, nullable=False)

    reasoning_score = Column(Float, nullable=False)
    reasoning_feedback = Column(Text, nullable=False)

    balance_score = Column(Float, nullable=False)
    balance_feedback = Column(Text, nullable=False)

    communication_score = Column(Float, nullable=False)
    communication_feedback = Column(Text, nullable=False)

    # Overall Summary
    overall_score = Column(Float, nullable=False, index=True)
    overall_feedback = Column(Text, nullable=False)

    # Key Insights & Suggested Model Response
    strengths = Column(JSON, nullable=False, default=list)
    areas_to_improve = Column(JSON, nullable=False, default=list)
    suggested_answer = Column(Text, nullable=False)

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

    # Relationship
    answer = relationship("InterviewAnswer", back_populates="evaluation")
