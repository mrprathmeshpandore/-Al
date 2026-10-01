"""
Coach API Router for Prashasak AI.

Endpoints for retrieving and generating daily/weekly preparation plans,
tracking task completions, and managing AI recommendations.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.routers.auth import get_current_user
from app.models.user import User
from app.schemas.coach import (
    PlanResponse,
    TodayPlanResponse,
    GeneratePlanRequest,
    TaskActionResponse,
)
from app.services.coach.coach_service import CoachService

router = APIRouter(prefix="/coach", tags=["coach"])
coach_service = CoachService()


@router.get("/today", response_model=TodayPlanResponse)
def get_today_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve active tasks and plan status for today."""
    return coach_service.get_today_plan(db, current_user.id)


@router.get("/plans", response_model=List[PlanResponse])
def get_plans(
    plan_type: Optional[str] = Query(None, alias="type", description="DAILY, WEEKLY, or CUSTOM"),
    plan_status: Optional[str] = Query(None, alias="status", description="ACTIVE, COMPLETED, or ARCHIVED"),
    target_date: Optional[str] = Query(None, alias="date", description="YYYY-MM-DD"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve candidate's preparation plans with optional filtering."""
    return coach_service.get_user_plans(
        db,
        current_user.id,
        plan_type=plan_type,
        status=plan_status,
        date_str=target_date,
        skip=skip,
        limit=limit,
    )


@router.get("/plans/{plan_id}", response_model=PlanResponse)
def get_plan_by_id(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve a specific preparation plan by ID with strict user isolation."""
    plan = coach_service.get_plan_by_id(db, current_user.id, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preparation plan not found or unauthorized access.",
        )
    return plan


@router.post("/daily-plan", response_model=PlanResponse)
def generate_daily_plan(
    payload: Optional[GeneratePlanRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a personalized daily preparation plan."""
    refresh = payload.refresh if payload else False
    return coach_service.generate_daily_plan(db, current_user.id, refresh=refresh)


@router.post("/weekly-plan", response_model=PlanResponse)
def generate_weekly_plan(
    payload: Optional[GeneratePlanRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a personalized 7-day preparation plan."""
    refresh = payload.refresh if payload else False
    return coach_service.generate_weekly_plan(db, current_user.id, refresh=refresh)


@router.post("/refresh", response_model=PlanResponse)
def refresh_coach(
    payload: Optional[GeneratePlanRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Force regenerate preparation plan using candidate's latest analytics."""
    plan_type = payload.plan_type.upper() if payload and payload.plan_type else "DAILY"
    if plan_type == "WEEKLY":
        return coach_service.generate_weekly_plan(db, current_user.id, refresh=True)
    return coach_service.generate_daily_plan(db, current_user.id, refresh=True)


@router.post("/tasks/{task_id}/start", response_model=TaskActionResponse)
def start_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a preparation task as in-progress."""
    res = coach_service.start_task(db, current_user.id, task_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or unauthorized access.",
        )
    return res


@router.post("/tasks/{task_id}/complete", response_model=TaskActionResponse)
def complete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a preparation task as completed."""
    res = coach_service.complete_task(db, current_user.id, task_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or unauthorized access.",
        )
    return res


@router.post("/tasks/{task_id}/skip", response_model=TaskActionResponse)
def skip_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a preparation task as skipped."""
    res = coach_service.skip_task(db, current_user.id, task_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or unauthorized access.",
        )
    return res
