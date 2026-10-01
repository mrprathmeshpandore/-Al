from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class AnalyticsOverview(BaseModel):
    """Schema for high-level candidate practice and performance overview."""
    total_questions_practiced: int = Field(default=0, description="Count of unique session questions served to candidate")
    total_interviews_started: int = Field(default=0, description="Total interview sessions initiated")
    total_interviews_completed: int = Field(default=0, description="Total interview sessions marked COMPLETED")
    total_answers: int = Field(default=0, description="Total candidate answers submitted")
    total_evaluated_answers: int = Field(default=0, description="Total candidate answers evaluated by AI")
    average_score: Optional[float] = Field(default=None, description="Average overall evaluation score (null if no evaluations)")
    highest_score: Optional[float] = Field(default=None, description="Highest overall evaluation score (null if no evaluations)")
    lowest_score: Optional[float] = Field(default=None, description="Lowest overall evaluation score (null if no evaluations)")
    current_streak: int = Field(default=0, description="Current consecutive practice days streak")
    longest_streak: int = Field(default=0, description="Longest consecutive practice days streak")
    practice_days: int = Field(default=0, description="Total distinct calendar practice days")
    voice_answers: int = Field(default=0, description="Count of answers submitted via voice mode")
    text_answers: int = Field(default=0, description="Count of answers submitted via text mode")
    voice_percentage: float = Field(default=0.0, description="Percentage of voice answers")
    text_percentage: float = Field(default=0.0, description="Percentage of text answers")


class SkillItem(BaseModel):
    """Schema for individual evaluation dimension performance."""
    name: str = Field(..., description="Dimension name: Content, Clarity, Depth, Reasoning, Balance, Communication")
    average_score: Optional[float] = Field(default=None, description="Average score (null if no evaluations)")
    evaluated_answers_count: int = Field(default=0, description="Count of evaluated answers for this skill")
    trend: Optional[float] = Field(default=None, description="Recent score trend change (+/- float)")


class SkillAnalytics(BaseModel):
    """Schema for full 6-dimensional skill analysis breakdown."""
    content: SkillItem
    clarity: SkillItem
    depth: SkillItem
    reasoning: SkillItem
    balance: SkillItem
    communication: SkillItem


class TrendPoint(BaseModel):
    """Schema for historical score trend data point."""
    date: str = Field(..., description="Date string YYYY-MM-DD")
    average_score: float = Field(..., description="Average score for that date")
    evaluated_answers: int = Field(..., description="Evaluated answers count on that date")


class ScoreTrendResponse(BaseModel):
    """Schema for score trend API response."""
    period: str = Field(default="30d", description="Time period filter")
    points: List[TrendPoint] = Field(default_factory=list, description="Chronological trend points")


class TopicPerformanceItem(BaseModel):
    """Schema for performance by UPSC subject/topic category."""
    topic: str = Field(..., description="Topic or category name")
    average_score: Optional[float] = Field(default=None, description="Average overall score in this topic")
    questions_attempted: int = Field(default=0, description="Total questions attempted in topic")
    evaluated_answers: int = Field(default=0, description="Evaluated answers in topic")
    strongest_dimension: Optional[str] = Field(default=None, description="Highest scoring dimension in topic")
    weakest_dimension: Optional[str] = Field(default=None, description="Lowest scoring dimension in topic")


class QuestionTypeItem(BaseModel):
    """Schema for question type performance (MAIN, FOLLOW_UP, COUNTER, etc.)."""
    type: str = Field(..., description="Question type identifier")
    count: int = Field(default=0, description="Count of questions of this type")
    average_score: Optional[float] = Field(default=None, description="Average evaluation score")


class AdaptiveAnalytics(BaseModel):
    """Schema for adaptive follow-up and counter question statistics."""
    main_questions: int = Field(default=0, description="Depth 0 main questions served")
    follow_up_questions: int = Field(default=0, description="Depth 1 follow-up questions served")
    counter_questions: int = Field(default=0, description="Depth 2 counter questions served")
    average_follow_up_score: Optional[float] = Field(default=None, description="Average score on follow-up questions")
    average_counter_score: Optional[float] = Field(default=None, description="Average score on counter questions")
    follow_up_trigger_rate: float = Field(default=0.0, description="Follow-up trigger rate percentage")
    counter_trigger_rate: float = Field(default=0.0, description="Counter-question trigger rate percentage")


class WeakArea(BaseModel):
    """Schema for identified weak dimension requiring practice focus."""
    dimension: str = Field(..., description="Weak dimension name")
    average_score: float = Field(..., description="Average score in weak dimension")
    sample_size: int = Field(..., description="Evaluated answers count")
    recent_score: Optional[float] = Field(default=None, description="Most recent answer score")
    improvement_needed: str = Field(..., description="Actionable recommendation message")


class StrongArea(BaseModel):
    """Schema for identified strong dimension excellence."""
    dimension: str = Field(..., description="Strong dimension name")
    average_score: float = Field(..., description="Average score in strong dimension")
    sample_size: int = Field(..., description="Evaluated answers count")


class ActivityPoint(BaseModel):
    """Schema for daily practice activity chart."""
    date: str = Field(..., description="Date YYYY-MM-DD")
    questions_answered: int = Field(default=0, description="Questions answered on date")
    interviews_completed: int = Field(default=0, description="Interviews completed on date")


class AnalyticsHistoryItem(BaseModel):
    """Schema for session record item in analytics history."""
    session_id: str
    interview_type: str
    input_mode: str = "TEXT"
    status: str
    total_questions: int
    answered_questions: int
    evaluated_answers: int
    average_score: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AnalyticsHistoryResponse(BaseModel):
    """Schema for paginated session history analytics."""
    items: List[AnalyticsHistoryItem]
    total: int
    page: int
    page_size: int
    pages: int


class AnalyticsDashboard(BaseModel):
    """Combined aggregate analytics payload for Progress page integration."""
    overview: AnalyticsOverview
    skills: SkillAnalytics
    recent_trend: List[TrendPoint] = Field(default_factory=list)
    topics: List[TopicPerformanceItem] = Field(default_factory=list)
    question_types: List[QuestionTypeItem] = Field(default_factory=list)
    adaptive: AdaptiveAnalytics
    weak_areas: List[WeakArea] = Field(default_factory=list)
    strong_areas: List[StrongArea] = Field(default_factory=list)
    recent_activity: List[ActivityPoint] = Field(default_factory=list)
    recent_interviews: List[AnalyticsHistoryItem] = Field(default_factory=list)
