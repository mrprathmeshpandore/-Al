from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class TaskItemResponse(BaseModel):
    """Schema for an individual practice task item."""
    id: str
    plan_id: str
    task_type: str
    title: str
    description: Optional[str] = None
    priority: str = "MEDIUM"
    estimated_minutes: int = 15
    target_date: str
    status: str = "PENDING"
    source_type: Optional[str] = None
    source_id: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PlanResponse(BaseModel):
    """Schema for a preparation plan with nested tasks."""
    id: str
    plan_type: str
    status: str
    title: str
    summary: Optional[str] = None
    target_date: str
    created_at: datetime
    tasks: List[TaskItemResponse] = Field(default_factory=list)
    completion_percentage: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class TodayPlanResponse(BaseModel):
    """Schema for candidate's active daily dashboard task response."""
    date: str
    plan: Optional[PlanResponse] = None
    tasks: List[TaskItemResponse] = Field(default_factory=list)
    total_tasks: int = 0
    completed_tasks: int = 0


class GeneratePlanRequest(BaseModel):
    """Request payload to trigger daily or weekly plan generation."""
    plan_type: str = Field(default="DAILY", description="DAILY or WEEKLY")
    refresh: bool = Field(default=False, description="Force regenerate plan with latest analytics")


class TaskActionResponse(BaseModel):
    """Response payload for task status transitions (start, complete, skip)."""
    task_id: str
    status: str
    completed_at: Optional[datetime] = None


# Gemini Structured JSON Parsing Schemas
class GeminiFocusArea(BaseModel):
    area: str
    priority: str = "HIGH"
    reason: str


class GeminiTaskItem(BaseModel):
    task_type: str = "QUESTION_PRACTICE"
    title: str
    description: str
    priority: str = "MEDIUM"
    estimated_minutes: int = 15
    source_type: Optional[str] = None
    source_id: Optional[str] = None


class GeminiCoachOutput(BaseModel):
    plan_title: str
    summary: str
    focus_areas: List[GeminiFocusArea] = Field(default_factory=list)
    tasks: List[GeminiTaskItem] = Field(default_factory=list)
