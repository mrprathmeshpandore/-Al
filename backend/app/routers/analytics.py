from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.analytics import (
    AnalyticsOverview,
    SkillAnalytics,
    ScoreTrendResponse,
    TopicPerformanceItem,
    AdaptiveAnalytics,
    WeakArea,
    StrongArea,
    ActivityPoint,
    AnalyticsHistoryResponse,
    AnalyticsDashboard,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Candidate Performance Analytics Engine"])


@router.get("/overview", response_model=AnalyticsOverview)
def get_analytics_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve aggregate practice, interview, evaluation, streak, and mode statistics for current user."""
    service = AnalyticsService(db)
    return service.get_overview(current_user.id)


@router.get("/skills", response_model=SkillAnalytics)
def get_skill_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve 6-dimensional evaluation breakdown (Content, Clarity, Depth, Reasoning, Balance, Communication)."""
    service = AnalyticsService(db)
    return service.get_skill_analysis(current_user.id)


@router.get("/trends", response_model=ScoreTrendResponse)
def get_score_trends(
    period: str = Query("30d", description="Time window for trends: 30d, 90d, 1y"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve historical score evaluation trend points for current user."""
    service = AnalyticsService(db)
    return service.get_score_trend(current_user.id, period=period)


@router.get("/topics", response_model=List[TopicPerformanceItem])
def get_topic_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve performance metrics grouped by UPSC topic and subject category."""
    service = AnalyticsService(db)
    return service.get_topic_performance(current_user.id)


@router.get("/adaptive", response_model=AdaptiveAnalytics)
def get_adaptive_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve adaptive follow-up and counter-questioning statistics and trigger rates."""
    service = AnalyticsService(db)
    return service.get_adaptive_stats(current_user.id)


@router.get("/weak-areas", response_model=List[WeakArea])
def get_weak_areas(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Identify weak evaluation dimensions needing focus based on score threshold and minimum sample size."""
    service = AnalyticsService(db)
    return service.get_weak_areas(current_user.id)


@router.get("/strong-areas", response_model=List[StrongArea])
def get_strong_areas(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Identify strong evaluation dimensions exceeding performance thresholds."""
    service = AnalyticsService(db)
    return service.get_strong_areas(current_user.id)


@router.get("/activity", response_model=List[ActivityPoint])
def get_practice_activity(
    days: int = Query(30, ge=1, le=365, description="Lookback window in days"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve daily practice activity timeline."""
    service = AnalyticsService(db)
    return service.get_practice_activity(current_user.id, days=days)


@router.get("/history", response_model=AnalyticsHistoryResponse)
def get_interview_history_analytics(
    status: Optional[str] = Query(None, description="Filter by session status"),
    interview_type: Optional[str] = Query(None, description="Filter by interview type"),
    input_mode: Optional[str] = Query(None, description="Filter by input mode: TEXT or VOICE"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve paginated session history with interview-level score averages."""
    service = AnalyticsService(db)
    return service.get_interview_history(
        user_id=current_user.id,
        status=status,
        interview_type=interview_type,
        input_mode=input_mode,
        page=page,
        page_size=page_size,
    )


@router.get("/dashboard", response_model=AnalyticsDashboard)
def get_analytics_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve complete combined analytics payload for Progress Page integration."""
    service = AnalyticsService(db)
    return service.get_dashboard(current_user.id)
