"""
Plan Service for AI Preparation Coach.

Manages preparation plans, tasks, idempotency, user isolation,
and status transitions.
"""

from datetime import date, datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.coach import (
    PreparationPlan,
    PreparationTask,
    PlanType,
    PlanStatus,
    TaskType,
    TaskPriority,
    TaskStatus,
)
from app.schemas.coach import GeminiCoachOutput, GeminiTaskItem, PlanResponse, TaskItemResponse, TodayPlanResponse


class PlanService:
    @staticmethod
    def _compute_completion_percentage(tasks: List[PreparationTask]) -> float:
        if not tasks:
            return 0.0
        completed_count = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED.value)
        return round((completed_count / len(tasks)) * 100.0, 1)

    @classmethod
    def format_plan_response(cls, plan: PreparationPlan) -> Dict[str, Any]:
        tasks_list = [
            TaskItemResponse(
                id=t.id,
                plan_id=t.plan_id,
                task_type=t.task_type,
                title=t.title,
                description=t.description,
                priority=t.priority,
                estimated_minutes=t.estimated_minutes,
                target_date=t.target_date.isoformat(),
                status=t.status,
                source_type=t.source_type,
                source_id=t.source_id,
                created_at=t.created_at,
                completed_at=t.completed_at,
            )
            for t in plan.tasks
        ]
        completion_pct = cls._compute_completion_percentage(plan.tasks)
        return {
            "id": plan.id,
            "plan_type": plan.plan_type,
            "status": plan.status,
            "title": plan.title,
            "summary": plan.summary,
            "target_date": plan.target_date.isoformat(),
            "created_at": plan.created_at,
            "tasks": tasks_list,
            "completion_percentage": completion_pct,
        }

    @classmethod
    def get_today_plan(cls, db: Session, user_id: str) -> Dict[str, Any]:
        """Get active plan and tasks for today."""
        today = date.today()

        # Find active plan matching today's target date
        plan = (
            db.query(PreparationPlan)
            .filter(
                PreparationPlan.user_id == user_id,
                PreparationPlan.target_date == today,
                PreparationPlan.status == PlanStatus.ACTIVE.value,
            )
            .order_by(desc(PreparationPlan.created_at))
            .first()
        )

        # Fallback: find any active plan created today or most recent active plan
        if not plan:
            plan = (
                db.query(PreparationPlan)
                .filter(
                    PreparationPlan.user_id == user_id,
                    PreparationPlan.status == PlanStatus.ACTIVE.value,
                )
                .order_by(desc(PreparationPlan.created_at))
                .first()
            )

        if not plan:
            return {
                "date": today.isoformat(),
                "plan": None,
                "tasks": [],
                "total_tasks": 0,
                "completed_tasks": 0,
            }

        plan_resp = cls.format_plan_response(plan)
        tasks = plan_resp["tasks"]
        completed_count = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED.value)

        return {
            "date": today.isoformat(),
            "plan": plan_resp,
            "tasks": tasks,
            "total_tasks": len(tasks),
            "completed_tasks": completed_count,
        }

    @classmethod
    def get_user_plans(
        cls,
        db: Session,
        user_id: str,
        plan_type: Optional[str] = None,
        status: Optional[str] = None,
        date_str: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        query = db.query(PreparationPlan).filter(PreparationPlan.user_id == user_id)

        if plan_type:
            query = query.filter(PreparationPlan.plan_type == plan_type.upper())
        if status:
            query = query.filter(PreparationPlan.status == status.upper())
        if date_str:
            try:
                target_dt = datetime.strptime(date_str, "%Y-%m-%d").date()
                query = query.filter(PreparationPlan.target_date == target_dt)
            except ValueError:
                pass

        plans = query.order_by(desc(PreparationPlan.created_at)).offset(skip).limit(limit).all()
        return [cls.format_plan_response(p) for p in plans]

    @classmethod
    def get_plan_by_id(cls, db: Session, user_id: str, plan_id: str) -> Optional[Dict[str, Any]]:
        plan = (
            db.query(PreparationPlan)
            .filter(PreparationPlan.id == plan_id, PreparationPlan.user_id == user_id)
            .first()
        )
        if not plan:
            return None
        return cls.format_plan_response(plan)

    @classmethod
    def get_active_plan(cls, db: Session, user_id: str, plan_type: str, target_date: date) -> Optional[PreparationPlan]:
        """Find active plan for user for a given plan type and target date."""
        return (
            db.query(PreparationPlan)
            .filter(
                PreparationPlan.user_id == user_id,
                PreparationPlan.plan_type == plan_type,
                PreparationPlan.target_date == target_date,
                PreparationPlan.status == PlanStatus.ACTIVE.value,
            )
            .order_by(desc(PreparationPlan.created_at))
            .first()
        )

    @classmethod
    def create_plan_with_tasks(
        cls,
        db: Session,
        user_id: str,
        plan_type: str,
        recommendation: GeminiCoachOutput,
        target_date: date,
        refresh: bool = False,
    ) -> Dict[str, Any]:
        """
        Create a new preparation plan with tasks from Gemini recommendations.
        Enforces idempotency: if refresh=False and active plan exists, returns existing plan.
        If refresh=True, archives previous active plan of same type and creates a fresh plan.
        """
        valid_plan_type = plan_type.upper() if plan_type.upper() in [p.value for p in PlanType] else PlanType.DAILY.value

        # Check existing active plan for idempotency
        existing_plan = cls.get_active_plan(db, user_id, valid_plan_type, target_date)
        if existing_plan and not refresh:
            return cls.format_plan_response(existing_plan)

        # Archive old active plans of the same type if refreshing
        if existing_plan and refresh:
            old_plans = (
                db.query(PreparationPlan)
                .filter(
                    PreparationPlan.user_id == user_id,
                    PreparationPlan.plan_type == valid_plan_type,
                    PreparationPlan.status == PlanStatus.ACTIVE.value,
                )
                .all()
            )
            for old_p in old_plans:
                old_p.status = PlanStatus.ARCHIVED.value
            db.flush()

        # Create new plan
        new_plan = PreparationPlan(
            user_id=user_id,
            plan_type=valid_plan_type,
            status=PlanStatus.ACTIVE.value,
            title=recommendation.plan_title[:250],
            summary=recommendation.summary,
            target_date=target_date,
        )
        db.add(new_plan)
        db.flush()

        # Valid enum lookup sets
        valid_task_types = {t.value for t in TaskType}
        valid_priorities = {p.value for p in TaskPriority}

        # Create tasks
        task_objs = []
        tasks_data = recommendation.tasks[:10]  # Bounded max 10 tasks

        for idx, task_data in enumerate(tasks_data):
            # Validate task fields
            task_type = task_data.task_type.upper() if task_data.task_type and task_data.task_type.upper() in valid_task_types else TaskType.QUESTION_PRACTICE.value
            priority = task_data.priority.upper() if task_data.priority and task_data.priority.upper() in valid_priorities else TaskPriority.MEDIUM.value
            estimated_minutes = max(5, min(120, task_data.estimated_minutes or 15))

            # For weekly plans, spread tasks across days
            if valid_plan_type == PlanType.WEEKLY.value:
                day_offset = min(idx // 2, 6)
                task_target_date = target_date + timedelta(days=day_offset)
            else:
                task_target_date = target_date

            t_obj = PreparationTask(
                plan_id=new_plan.id,
                user_id=user_id,
                task_type=task_type,
                title=task_data.title[:250],
                description=task_data.description,
                priority=priority,
                estimated_minutes=estimated_minutes,
                target_date=task_target_date,
                status=TaskStatus.PENDING.value,
                source_type=task_data.source_type,
                source_id=task_data.source_id,
            )
            db.add(t_obj)
            task_objs.append(t_obj)

        db.commit()
        db.refresh(new_plan)
        return cls.format_plan_response(new_plan)

    @classmethod
    def update_task_status(
        cls, db: Session, user_id: str, task_id: str, new_status: str
    ) -> Optional[Dict[str, Any]]:
        """
        Update task status with strict user isolation.
        Valid status transitions: PENDING -> IN_PROGRESS / COMPLETED / SKIPPED.
        """
        task = (
            db.query(PreparationTask)
            .filter(PreparationTask.id == task_id, PreparationTask.user_id == user_id)
            .first()
        )
        if not task:
            return None

        valid_statuses = {s.value for s in TaskStatus}
        if new_status not in valid_statuses:
            return None

        task.status = new_status
        if new_status == TaskStatus.COMPLETED.value:
            task.completed_at = datetime.now(timezone.utc)
        elif new_status in (TaskStatus.PENDING.value, TaskStatus.IN_PROGRESS.value):
            task.completed_at = None

        db.commit()
        db.refresh(task)

        # Check if parent plan complete
        plan = db.query(PreparationPlan).filter(PreparationPlan.id == task.plan_id).first()
        if plan and plan.tasks:
            all_done = all(
                t.status in (TaskStatus.COMPLETED.value, TaskStatus.SKIPPED.value) for t in plan.tasks
            )
            if all_done:
                plan.status = PlanStatus.COMPLETED.value
                db.commit()

        return {
            "task_id": task.id,
            "status": task.status,
            "completed_at": task.completed_at,
        }
