from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class EvaluationDimension(BaseModel):
    score: float = Field(..., ge=0.0, le=10.0, description="Dimension score from 0 to 10")
    feedback: str = Field(..., min_length=1, max_length=2000, description="Specific feedback for this dimension")


class EvaluationResult(BaseModel):
    content: EvaluationDimension
    clarity: EvaluationDimension
    depth: EvaluationDimension
    reasoning: EvaluationDimension
    balance: EvaluationDimension
    communication: EvaluationDimension
    overall_feedback: str = Field(..., min_length=1, max_length=5000, description="Comprehensive overall assessment summary")
    strengths: List[str] = Field(default_factory=list, description="Key candidate strengths observed in the answer")
    areas_to_improve: List[str] = Field(default_factory=list, description="Actionable recommendations for improvement")
    suggested_answer: str = Field(..., min_length=1, max_length=10000, description="Suggested structured model answer")


class EvaluationResponse(BaseModel):
    id: str
    answer_id: str
    content: EvaluationDimension
    clarity: EvaluationDimension
    depth: EvaluationDimension
    reasoning: EvaluationDimension
    balance: EvaluationDimension
    communication: EvaluationDimension
    overall_score: float = Field(..., ge=0.0, le=10.0, description="Weighted overall score calculated authoritatively by backend")
    overall_feedback: str
    strengths: List[str]
    areas_to_improve: List[str]
    suggested_answer: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
