from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator

VALID_QUESTION_TYPES = {"MAIN", "FOLLOW_UP", "COUNTER", "ETHICAL", "SCENARIO"}
VALID_DIFFICULTIES = {"EASY", "MODERATE", "HARD"}
VALID_PERSONALIZATION_SOURCES = {
    "EDUCATION",
    "HOMETOWN",
    "CURRENT_CITY",
    "OPTIONAL_SUBJECT",
    "UPSC_JOURNEY",
    "HOBBY",
    "SPORT",
    "BOOK",
    "INTEREST",
    "SOCIAL_ACTIVITY",
    "PERSPECTIVE",
    "WORK_EXPERIENCE",
    "GENERAL_DAF",
}


class QuestionGenerateRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=255, description="UPSC topic or subject area for practice question")
    subject: Optional[str] = Field(default=None, max_length=100, description="UPSC core subject area (e.g. Polity, History, Economy)")
    category: Optional[str] = Field(default=None, max_length=100, description="Resource or subject sub-category")
    difficulty: Optional[str] = Field(default="MODERATE", description="Difficulty level: EASY, MODERATE, or HARD")
    question_type: Optional[str] = Field(default="MAIN", description="Interview question type: MAIN, FOLLOW_UP, COUNTER, ETHICAL, SCENARIO")
    top_k: Optional[int] = Field(default=5, ge=1, le=10, description="Number of top RAG chunks to retrieve for question grounding")

    @field_validator("topic")
    @classmethod
    def validate_topic_non_empty(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Topic must not be empty or whitespace only.")
        return clean

    @field_validator("question_type")
    @classmethod
    def validate_question_type(cls, v: Optional[str]) -> str:
        if not v:
            return "MAIN"
        upper = v.upper().strip()
        if upper not in VALID_QUESTION_TYPES:
            raise ValueError(f"Invalid question_type '{v}'. Allowed types: {', '.join(sorted(VALID_QUESTION_TYPES))}")
        return upper

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: Optional[str]) -> str:
        if not v:
            return "MODERATE"
        upper = v.upper().strip()
        if upper not in VALID_DIFFICULTIES:
            raise ValueError(f"Invalid difficulty '{v}'. Allowed values: {', '.join(sorted(VALID_DIFFICULTIES))}")
        return upper


class PersonalizedQuestionGenerateRequest(BaseModel):
    source: Optional[str] = Field(default=None, description="DAF module field to generate question from")
    personalization_source: Optional[str] = Field(default=None, description="DAF module field to generate question from")
    difficulty: Optional[str] = Field(default="MODERATE", description="Difficulty level: EASY, MODERATE, or HARD")
    question_type: Optional[str] = Field(default="MAIN", description="Interview question type: MAIN, FOLLOW_UP, COUNTER, ETHICAL, SCENARIO")
    top_k: Optional[int] = Field(default=5, ge=1, le=10, description="Number of top RAG chunks to retrieve for question grounding")

    @field_validator("source", "personalization_source", mode="before")
    @classmethod
    def validate_source(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return v
        upper = v.upper().strip()
        if upper not in VALID_PERSONALIZATION_SOURCES:
            raise ValueError(f"Invalid personalization source '{v}'. Allowed values: {', '.join(sorted(VALID_PERSONALIZATION_SOURCES))}")
        return upper

    @model_validator(mode="after")
    def populate_source(self) -> "PersonalizedQuestionGenerateRequest":
        if not self.source and self.personalization_source:
            self.source = self.personalization_source
        elif not self.personalization_source and self.source:
            self.personalization_source = self.source
        elif not self.source and not self.personalization_source:
            self.source = "EDUCATION"
            self.personalization_source = "EDUCATION"
        return self

    @field_validator("question_type")
    @classmethod
    def validate_question_type(cls, v: Optional[str]) -> str:
        if not v:
            return "MAIN"
        upper = v.upper().strip()
        if upper not in VALID_QUESTION_TYPES:
            raise ValueError(f"Invalid question_type '{v}'. Allowed types: {', '.join(sorted(VALID_QUESTION_TYPES))}")
        return upper

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: Optional[str]) -> str:
        if not v:
            return "MODERATE"
        upper = v.upper().strip()
        if upper not in VALID_DIFFICULTIES:
            raise ValueError(f"Invalid difficulty '{v}'. Allowed values: {', '.join(sorted(VALID_DIFFICULTIES))}")
        return upper


class QuestionSourceSchema(BaseModel):
    resource_id: Optional[str] = Field(None, description="Resource ID")
    document_id: Optional[str] = Field(None, description="Document ID")
    chunk_id: Optional[str] = Field(None, description="Document Chunk ID")
    resource_title: str = Field(..., description="Title of parent knowledge resource")
    page_number: Optional[int] = Field(None, description="Page number in PDF document")
    chunk_index: Optional[int] = Field(None, description="Chunk index in document")
    score: Optional[float] = Field(None, description="Cosine similarity score")


class QuestionResponse(BaseModel):
    id: Optional[str] = Field(default=None, description="Unique question ID")
    question: str = Field(..., description="Interview practice question text")
    question_type: str = Field(..., description="Question type (MAIN, FOLLOW_UP, COUNTER, ETHICAL, SCENARIO)")
    difficulty: str = Field(..., description="Difficulty level (EASY, MODERATE, HARD)")
    subject: Optional[str] = Field(None, description="Core subject area")
    topic: Optional[str] = Field(None, description="Specific topic")
    category: Optional[str] = Field(None, description="Sub-category")
    is_personalized: bool = Field(default=False, description="True if generated from candidate's DAF profile")
    personalization_source: Optional[str] = Field(default=None, description="DAF module source type")
    personalization_label: Optional[str] = Field(default=None, description="Label for candidate DAF background")
    why_this_matters: Optional[str] = Field(None, description="Contextual significance for UPSC personality test")
    explanation: Optional[str] = Field(None, description="Analytical background / perspective explanation")
    grounded: bool = Field(True, description="True if question is grounded in retrieved knowledge base chunks")
    sources: List[QuestionSourceSchema] = Field(default_factory=list, description="Backend-verified citation metadata sources")
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp when question was generated")


class QuestionListResponse(BaseModel):
    total: int = Field(..., description="Total count of questions matching criteria")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Page size limit")
    questions: List[QuestionResponse] = Field(default_factory=list, description="List of interview practice questions")
