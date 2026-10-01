from typing import Optional
from pydantic import BaseModel, Field


class FollowupDecisionSchema(BaseModel):
    should_follow_up: bool = Field(..., description="Whether a follow-up question is required based on candidate answer")
    reason: Optional[str] = Field(None, description="Concise operational reason for the follow-up decision")
    follow_up_type: Optional[str] = Field("FOLLOW_UP", description="Question type (FOLLOW_UP, ETHICAL, SCENARIO)")
    question: Optional[str] = Field(None, description="Generated follow-up question text if required")


class CounterDecisionSchema(BaseModel):
    should_counter: bool = Field(..., description="Whether a counter question is required to test defence of position")
    reason: Optional[str] = Field(None, description="Concise operational reason for counter decision")
    counter_type: Optional[str] = Field("COUNTER", description="Question type (COUNTER, ETHICAL, SCENARIO)")
    question: Optional[str] = Field(None, description="Generated counter question text if required")
