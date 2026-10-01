from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict


class PotentialQuestionResponse(BaseModel):
    id: str
    question_text: str
    question_type: str
    difficulty: str
    explanation: Optional[str] = None
    why_this_matters: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CurrentAffairBase(BaseModel):
    title: str
    source_name: str
    source_url: Optional[str] = None
    category: str = "NATIONAL"
    topic: Optional[str] = None
    subtopic: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None


class CurrentAffairCreate(CurrentAffairBase):
    published_at: Optional[datetime] = None


class CurrentAffairResponse(BaseModel):
    id: str
    title: str
    slug: str
    summary: Optional[str] = None
    source_name: str
    source_url: Optional[str] = None
    published_at: Optional[datetime] = None
    retrieved_at: datetime
    category: str
    categoryLabel: Optional[str] = None
    topic: Optional[str] = None
    subtopic: Optional[str] = None
    content: Optional[str] = None
    key_points: List[str] = Field(default_factory=list)
    context: Optional[str] = None
    policy_response: Optional[str] = None
    upsc_relevance: Optional[str] = None
    interview_angle: Optional[str] = None
    analysis_status: str
    potential_questions: List[PotentialQuestionResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    # UI Alias fields for Frontend Compatibility
    source: Optional[str] = None
    date: Optional[str] = None
    whyItMatters: Optional[str] = None
    shortContext: Optional[str] = None
    keyPoints: List[str] = Field(default_factory=list)
    governmentResponse: Optional[str] = None
    upscRelevance: Optional[str] = None
    interviewAngle: Optional[str] = None
    potentialQuestions: List[Dict[str, Any]] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class CurrentAffairListResponse(BaseModel):
    items: List[CurrentAffairResponse]
    total: int
    page: int
    page_size: int
    pages: int


class CategoryItem(BaseModel):
    id: str
    name: str
    label: str


class CategoryListResponse(BaseModel):
    categories: List[CategoryItem]


class TopicListResponse(BaseModel):
    topics: List[str]
