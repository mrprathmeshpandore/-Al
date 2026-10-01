from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class InterviewStartRequest(BaseModel):
    interview_type: str = Field(default="FULL_INTERVIEW", description="Type of interview: FULL_INTERVIEW, QUICK_PRACTICE, DAF_INTERVIEW, CURRENT_AFFAIRS, CUSTOM")
    total_questions: int = Field(default=10, ge=1, le=20, description="Total questions for the session (1-20)")
    include_daf_questions: bool = Field(default=True, description="Include DAF personalized questions")
    include_current_affairs: bool = Field(default=True, description="Include current affairs questions")
    include_rag_questions: bool = Field(default=True, description="Include RAG grounded questions")
    include_adaptive: bool = Field(default=True, description="Include adaptive follow-up and counter questions")
    input_mode: str = Field(default="TEXT", description="Answer mode: TEXT or VOICE")
    language: str = Field(default="en-IN", description="Target voice language code")
    difficulty: str = Field(default="MODERATE", description="Difficulty level: EASY, MODERATE, CHALLENGING, HARD")
    topic: Optional[str] = Field(default=None, description="Optional target topic filter")
    category: Optional[str] = Field(default=None, description="Optional target category filter")


class AnswerSubmitRequest(BaseModel):
    answer_text: str = Field(..., min_length=1, max_length=10000, description="Candidate answer text")
    answer_duration_seconds: int = Field(default=0, ge=0, description="Answer duration in seconds")


class AdaptiveMetadata(BaseModel):
    is_adaptive: bool = False
    parent_question_id: Optional[str] = None
    parent_answer_id: Optional[str] = None
    depth: int = 0
    adaptive_type: Optional[str] = "MAIN"
    generated_reason: Optional[str] = None


class SessionQuestionItem(BaseModel):
    id: str
    sequence_number: int
    question_status: str
    text: str
    type: str
    difficulty: str
    category: Optional[str] = None
    topic: Optional[str] = None
    is_personalized: bool = False
    personalization_source: Optional[str] = None
    personalization_label: Optional[str] = None
    explanation: Optional[str] = None
    why_this_matters: Optional[str] = None
    question_depth: int = 0
    parent_session_question_id: Optional[str] = None
    parent_answer_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class InterviewSessionResponse(BaseModel):
    session_id: str
    status: str
    interview_type: str
    total_questions: int
    current_question_index: int
    input_mode: str = "TEXT"
    language: str = "en-IN"
    current_question: Optional[SessionQuestionItem] = None
    questions: List[SessionQuestionItem] = Field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnswerSubmitResponse(BaseModel):
    answer_id: str
    session_question_id: str
    submitted_at: datetime
    next_action: str  # NEXT_QUESTION or COMPLETE_INTERVIEW


class NextQuestionResponse(BaseModel):
    session_id: str
    question: SessionQuestionItem
    progress: Dict[str, int]
    adaptive: Optional[AdaptiveMetadata] = None
    questions: List[SessionQuestionItem] = Field(default_factory=list)


class InterviewCompleteResponse(BaseModel):
    session_id: str
    status: str
    completed_at: datetime
    total_questions: int
    answered_questions: int


class InterviewHistoryItem(BaseModel):
    session_id: str
    interview_type: str
    status: str
    total_questions: int
    answered_questions: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InterviewHistoryResponse(BaseModel):
    items: List[InterviewHistoryItem]
    total: int
    page: int
    page_size: int
    pages: int
