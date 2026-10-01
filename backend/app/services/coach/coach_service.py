"""
Coach Service module coordinating ContextBuilder, RecommendationService, and PlanService.
"""

from datetime import date
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.services.coach.context_builder import CoachContextBuilder
from app.services.coach.recommendation_service import RecommendationService
from app.services.coach.plan_service import PlanService
from app.models.coach import TaskStatus, PlanType
from app.services.gemini_service import BaseGeminiService


class CoachService:
    def __init__(self, gemini_service: Optional[BaseGeminiService] = None):
        self.recommendation_service = RecommendationService(gemini_service=gemini_service)

    def generate_daily_plan(self, db: Session, user_id: str, refresh: bool = False) -> Dict[str, Any]:
        """Generate or retrieve a daily preparation plan."""
        today = date.today()

        # Check existing active daily plan if not forcing refresh
        if not refresh:
            existing = PlanService.get_active_plan(db, user_id, PlanType.DAILY.value, today)
            if existing:
                return PlanService.format_plan_response(existing)

        # Build bounded candidate context
        context = CoachContextBuilder.build_candidate_context(db, user_id)

        # Generate recommendations via Gemini / Fallback
        recommendation = self.recommendation_service.generate_recommendations(context, plan_type="DAILY")

        # Persist plan & tasks
        return PlanService.create_plan_with_tasks(
            db=db,
            user_id=user_id,
            plan_type=PlanType.DAILY.value,
            recommendation=recommendation,
            target_date=today,
            refresh=refresh,
        )

    def generate_weekly_plan(self, db: Session, user_id: str, refresh: bool = False) -> Dict[str, Any]:
        """Generate or retrieve a weekly 7-day preparation plan."""
        today = date.today()

        # Check existing active weekly plan if not forcing refresh
        if not refresh:
            existing = PlanService.get_active_plan(db, user_id, PlanType.WEEKLY.value, today)
            if existing:
                return PlanService.format_plan_response(existing)

        # Build bounded candidate context
        context = CoachContextBuilder.build_candidate_context(db, user_id)

        # Generate recommendations via Gemini / Fallback
        recommendation = self.recommendation_service.generate_recommendations(context, plan_type="WEEKLY")

        # Persist plan & tasks
        return PlanService.create_plan_with_tasks(
            db=db,
            user_id=user_id,
            plan_type=PlanType.WEEKLY.value,
            recommendation=recommendation,
            target_date=today,
            refresh=refresh,
        )

    def get_today_plan(self, db: Session, user_id: str) -> Dict[str, Any]:
        """Retrieve candidate's active daily dashboard task response."""
        return PlanService.get_today_plan(db, user_id)

    def get_user_plans(
        self,
        db: Session,
        user_id: str,
        plan_type: Optional[str] = None,
        status: Optional[str] = None,
        date_str: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        return PlanService.get_user_plans(
            db, user_id, plan_type=plan_type, status=status, date_str=date_str, skip=skip, limit=limit
        )

    def get_plan_by_id(self, db: Session, user_id: str, plan_id: str) -> Optional[Dict[str, Any]]:
        return PlanService.get_plan_by_id(db, user_id, plan_id)

    def start_task(self, db: Session, user_id: str, task_id: str) -> Optional[Dict[str, Any]]:
        return PlanService.update_task_status(db, user_id, task_id, TaskStatus.IN_PROGRESS.value)

    def complete_task(self, db: Session, user_id: str, task_id: str) -> Optional[Dict[str, Any]]:
        return PlanService.update_task_status(db, user_id, task_id, TaskStatus.COMPLETED.value)

    def skip_task(self, db: Session, user_id: str, task_id: str) -> Optional[Dict[str, Any]]:
        return PlanService.update_task_status(db, user_id, task_id, TaskStatus.SKIPPED.value)
