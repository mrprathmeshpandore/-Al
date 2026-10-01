import uuid
from datetime import datetime, timezone, date
from enum import Enum
from sqlalchemy import Column, String, Text, Integer, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class PlanType(str, Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    CUSTOM = "CUSTOM"


class PlanStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class TaskType(str, Enum):
    QUESTION_PRACTICE = "QUESTION_PRACTICE"
    INTERVIEW_PRACTICE = "INTERVIEW_PRACTICE"
    CURRENT_AFFAIRS = "CURRENT_AFFAIRS"
    DAF_PRACTICE = "DAF_PRACTICE"
    RESOURCE_REVIEW = "RESOURCE_REVIEW"
    WEAK_AREA_PRACTICE = "WEAK_AREA_PRACTICE"
    FOLLOW_UP_PRACTICE = "FOLLOW_UP_PRACTICE"
    COUNTER_PRACTICE = "COUNTER_PRACTICE"
    REVISION = "REVISION"


class TaskPriority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"


class PreparationPlan(Base):
    __tablename__ = "preparation_plans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_type = Column(String(20), nullable=False, default=PlanType.DAILY.value, index=True)
    status = Column(String(20), nullable=False, default=PlanStatus.ACTIVE.value, index=True)
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=True)
    target_date = Column(Date, nullable=False, index=True)

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
    tasks = relationship("PreparationTask", back_populates="plan", cascade="all, delete-orphan", order_by="PreparationTask.id")


class PreparationTask(Base):
    __tablename__ = "preparation_tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plan_id = Column(String(36), ForeignKey("preparation_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    task_type = Column(String(50), nullable=False, default=TaskType.QUESTION_PRACTICE.value, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(20), nullable=False, default=TaskPriority.MEDIUM.value)
    estimated_minutes = Column(Integer, nullable=False, default=15)
    target_date = Column(Date, nullable=False, index=True)
    status = Column(String(20), nullable=False, default=TaskStatus.PENDING.value, index=True)
    source_type = Column(String(50), nullable=True)
    source_id = Column(String(100), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    plan = relationship("PreparationPlan", back_populates="tasks")
    user = relationship("User")
