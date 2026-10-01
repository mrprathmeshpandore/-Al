from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import func, case, distinct, desc, asc
from sqlalchemy.orm import Session

from app.models.interview import InterviewSession, InterviewSessionQuestion, InterviewAnswer, SessionStatus
from app.models.evaluation import InterviewAnswerEvaluation
from app.models.question import InterviewQuestion
from app.schemas.analytics import (
    AnalyticsOverview,
    SkillItem,
    SkillAnalytics,
    TrendPoint,
    ScoreTrendResponse,
    TopicPerformanceItem,
    QuestionTypeItem,
    AdaptiveAnalytics,
    WeakArea,
    StrongArea,
    ActivityPoint,
    AnalyticsHistoryItem,
    AnalyticsHistoryResponse,
    AnalyticsDashboard,
)

ANALYTICS_WEAK_SCORE_THRESHOLD = 6.0
ANALYTICS_STRONG_SCORE_THRESHOLD = 7.5
MINIMUM_SAMPLE_SIZE = 3


class AnalyticsService:
    """Service handling deterministic user-specific performance analytics calculations."""

    def __init__(self, db: Session):
        self.db = db

    def _get_user_evaluations_query(self, user_id: str):
        """Base query joining InterviewAnswerEvaluation to user's sessions."""
        return (
            self.db.query(InterviewAnswerEvaluation)
            .join(InterviewAnswer, InterviewAnswerEvaluation.answer_id == InterviewAnswer.id)
            .join(InterviewSessionQuestion, InterviewAnswer.session_question_id == InterviewSessionQuestion.id)
            .join(InterviewSession, InterviewSessionQuestion.session_id == InterviewSession.id)
            .filter(InterviewSession.user_id == user_id)
        )

    def _get_user_answers_query(self, user_id: str):
        """Base query joining InterviewAnswer to user's sessions."""
        return (
            self.db.query(InterviewAnswer)
            .join(InterviewSessionQuestion, InterviewAnswer.session_question_id == InterviewSessionQuestion.id)
            .join(InterviewSession, InterviewSessionQuestion.session_id == InterviewSession.id)
            .filter(InterviewSession.user_id == user_id)
        )

    def _calculate_streaks(self, user_id: str) -> tuple[int, int, int]:
        """Calculate current_streak, longest_streak, and total practice_days."""
        answers = (
            self._get_user_answers_query(user_id)
            .filter(InterviewAnswer.submitted_at.isnot(None))
            .all()
        )

        if not answers:
            return 0, 0, 0

        # Extract distinct YYYY-MM-DD dates
        dates = sorted(
            list(
                set(
                    ans.submitted_at.astimezone(timezone.utc).strftime("%Y-%m-%d")
                    for ans in answers
                    if ans.submitted_at
                )
            )
        )

        if not dates:
            return 0, 0, 0

        practice_days = len(dates)

        # Convert to date objects for streak calculation
        date_objs = [datetime.strptime(d, "%Y-%m-%d").date() for d in dates]

        longest_streak = 1
        current_streak = 0
        running_streak = 1

        for i in range(1, len(date_objs)):
            if (date_objs[i] - date_objs[i - 1]).days == 1:
                running_streak += 1
            else:
                running_streak = 1
            if running_streak > longest_streak:
                longest_streak = running_streak

        # Check if current streak extends to today or yesterday
        today = datetime.now(timezone.utc).date()
        yesterday = today - timedelta(days=1)

        last_practice_date = date_objs[-1]
        if last_practice_date in (today, yesterday):
            current_streak = 1
            idx = len(date_objs) - 1
            while idx > 0 and (date_objs[idx] - date_objs[idx - 1]).days == 1:
                current_streak += 1
                idx -= 1
        else:
            current_streak = 0

        return current_streak, longest_streak, practice_days

    def get_overview(self, user_id: str) -> AnalyticsOverview:
        """Calculate high-level practice and performance statistics."""
        # Total questions practiced (unique session questions served to user)
        total_questions_practiced = (
            self.db.query(func.count(distinct(InterviewSessionQuestion.id)))
            .join(InterviewSession, InterviewSessionQuestion.session_id == InterviewSession.id)
            .filter(InterviewSession.user_id == user_id)
            .scalar()
            or 0
        )

        # Total interviews started and completed
        session_counts = (
            self.db.query(
                func.count(InterviewSession.id).label("total"),
                func.sum(case((InterviewSession.status == SessionStatus.COMPLETED.value, 1), else_=0)).label("completed"),
            )
            .filter(InterviewSession.user_id == user_id)
            .first()
        )

        total_interviews_started = session_counts.total or 0 if session_counts else 0
        total_interviews_completed = int(session_counts.completed or 0) if session_counts else 0

        # Total answers submitted
        total_answers = (
            self._get_user_answers_query(user_id)
            .count()
        )

        # Score stats from evaluations
        eval_stats = (
            self._get_user_evaluations_query(user_id)
            .with_entities(
                func.count(InterviewAnswerEvaluation.id).label("count"),
                func.avg(InterviewAnswerEvaluation.overall_score).label("avg"),
                func.max(InterviewAnswerEvaluation.overall_score).label("max"),
                func.min(InterviewAnswerEvaluation.overall_score).label("min"),
            )
            .first()
        )

        total_evaluated_answers = eval_stats.count or 0 if eval_stats else 0
        average_score = round(float(eval_stats.avg), 1) if eval_stats and eval_stats.avg is not None else None
        highest_score = round(float(eval_stats.max), 1) if eval_stats and eval_stats.max is not None else None
        lowest_score = round(float(eval_stats.min), 1) if eval_stats and eval_stats.min is not None else None

        # Voice vs Text mode count
        input_counts = (
            self.db.query(
                InterviewSession.input_mode,
                func.count(InterviewAnswer.id),
            )
            .join(InterviewSessionQuestion, InterviewSessionQuestion.session_id == InterviewSession.id)
            .join(InterviewAnswer, InterviewAnswer.session_question_id == InterviewSessionQuestion.id)
            .filter(InterviewSession.user_id == user_id)
            .group_by(InterviewSession.input_mode)
            .all()
        )

        mode_dict = {mode.upper() if mode else "TEXT": count for mode, count in input_counts}
        voice_answers = mode_dict.get("VOICE", 0)
        text_answers = mode_dict.get("TEXT", 0)

        voice_percentage = round((voice_answers / total_answers) * 100.0, 1) if total_answers > 0 else 0.0
        text_percentage = round((text_answers / total_answers) * 100.0, 1) if total_answers > 0 else 0.0

        current_streak, longest_streak, practice_days = self._calculate_streaks(user_id)

        return AnalyticsOverview(
            total_questions_practiced=total_questions_practiced,
            total_interviews_started=total_interviews_started,
            total_interviews_completed=total_interviews_completed,
            total_answers=total_answers,
            total_evaluated_answers=total_evaluated_answers,
            average_score=average_score,
            highest_score=highest_score,
            lowest_score=lowest_score,
            current_streak=current_streak,
            longest_streak=longest_streak,
            practice_days=practice_days,
            voice_answers=voice_answers,
            text_answers=text_answers,
            voice_percentage=voice_percentage,
            text_percentage=text_percentage,
        )

    def get_skill_analysis(self, user_id: str) -> SkillAnalytics:
        """Calculate score averages and trends across all six evaluation dimensions."""
        evals = (
            self._get_user_evaluations_query(user_id)
            .order_by(asc(InterviewAnswerEvaluation.created_at))
            .all()
        )

        dimensions = ["content", "clarity", "depth", "reasoning", "balance", "communication"]
        skill_items = {}

        for dim in dimensions:
            scores = [getattr(e, f"{dim}_score") for e in evals if getattr(e, f"{dim}_score", None) is not None]
            count = len(scores)
            avg = round(sum(scores) / count, 1) if count > 0 else None

            trend = None
            if count >= 6:
                # Calculate trend between recent 5 and previous 5
                recent_5 = scores[-5:]
                prev_5 = scores[-10:-5]
                if prev_5:
                    recent_avg = sum(recent_5) / len(recent_5)
                    prev_avg = sum(prev_5) / len(prev_5)
                    trend = round(recent_avg - prev_avg, 1)

            skill_items[dim] = SkillItem(
                name=dim.capitalize(),
                average_score=avg,
                evaluated_answers_count=count,
                trend=trend,
            )

        return SkillAnalytics(**skill_items)

    def get_score_trend(self, user_id: str, period: str = "30d") -> ScoreTrendResponse:
        """Calculate historical score trend grouped by date."""
        days = 30
        if period == "90d":
            days = 90
        elif period == "1y":
            days = 365

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        evals = (
            self._get_user_evaluations_query(user_id)
            .filter(InterviewAnswerEvaluation.created_at >= cutoff)
            .order_by(asc(InterviewAnswerEvaluation.created_at))
            .all()
        )

        grouped: Dict[str, List[float]] = {}
        for e in evals:
            date_str = e.created_at.astimezone(timezone.utc).strftime("%Y-%m-%d")
            grouped.setdefault(date_str, []).append(e.overall_score)

        points = []
        for date_str, scores in sorted(grouped.items()):
            avg = round(sum(scores) / len(scores), 1)
            points.append(
                TrendPoint(
                    date=date_str,
                    average_score=avg,
                    evaluated_answers=len(scores),
                )
            )

        return ScoreTrendResponse(period=period, points=points)

    def get_topic_performance(self, user_id: str) -> List[TopicPerformanceItem]:
        """Aggregate performance grouped by question topic/category."""
        rows = (
            self.db.query(
                InterviewQuestion.category,
                InterviewQuestion.topic,
                InterviewAnswerEvaluation.overall_score,
                InterviewAnswerEvaluation.content_score,
                InterviewAnswerEvaluation.clarity_score,
                InterviewAnswerEvaluation.depth_score,
                InterviewAnswerEvaluation.reasoning_score,
                InterviewAnswerEvaluation.balance_score,
                InterviewAnswerEvaluation.communication_score,
            )
            .join(InterviewSessionQuestion, InterviewSessionQuestion.question_id == InterviewQuestion.id)
            .join(InterviewSession, InterviewSessionQuestion.session_id == InterviewSession.id)
            .outerjoin(InterviewAnswer, InterviewAnswer.session_question_id == InterviewSessionQuestion.id)
            .outerjoin(InterviewAnswerEvaluation, InterviewAnswerEvaluation.answer_id == InterviewAnswer.id)
            .filter(InterviewSession.user_id == user_id)
            .all()
        )

        topic_map: Dict[str, Dict[str, Any]] = {}
        for r in rows:
            topic_name = r.category or r.topic or "General Governance"
            if topic_name not in topic_map:
                topic_map[topic_name] = {
                    "attempted": 0,
                    "scores": [],
                    "dim_scores": {d: [] for d in ["content", "clarity", "depth", "reasoning", "balance", "communication"]},
                }

            topic_map[topic_name]["attempted"] += 1
            if r.overall_score is not None:
                topic_map[topic_name]["scores"].append(r.overall_score)
                for d in ["content", "clarity", "depth", "reasoning", "balance", "communication"]:
                    val = getattr(r, f"{d}_score")
                    if val is not None:
                        topic_map[topic_name]["dim_scores"][d].append(val)

        items = []
        for name, data in topic_map.items():
            scores = data["scores"]
            avg = round(sum(scores) / len(scores), 1) if scores else None

            strongest = None
            weakest = None
            if scores:
                dim_avgs = {}
                for d, d_scores in data["dim_scores"].items():
                    if d_scores:
                        dim_avgs[d] = sum(d_scores) / len(d_scores)
                if dim_avgs:
                    strongest = max(dim_avgs, key=dim_avgs.get).capitalize()
                    weakest = min(dim_avgs, key=dim_avgs.get).capitalize()

            items.append(
                TopicPerformanceItem(
                    topic=name,
                    average_score=avg,
                    questions_attempted=data["attempted"],
                    evaluated_answers=len(scores),
                    strongest_dimension=strongest,
                    weakest_dimension=weakest,
                )
            )

        items.sort(key=lambda x: (x.evaluated_answers, x.questions_attempted), reverse=True)
        return items

    def get_question_type_performance(self, user_id: str) -> List[QuestionTypeItem]:
        """Aggregate performance grouped by question type (MAIN, FOLLOW_UP, COUNTER)."""
        rows = (
            self.db.query(
                InterviewSessionQuestion.adaptive_type,
                InterviewAnswerEvaluation.overall_score,
            )
            .join(InterviewSession, InterviewSessionQuestion.session_id == InterviewSession.id)
            .outerjoin(InterviewAnswer, InterviewAnswer.session_question_id == InterviewSessionQuestion.id)
            .outerjoin(InterviewAnswerEvaluation, InterviewAnswerEvaluation.answer_id == InterviewAnswer.id)
            .filter(InterviewSession.user_id == user_id)
            .all()
        )

        type_map: Dict[str, List[float]] = {}
        type_count: Dict[str, int] = {}

        for r in rows:
            qtype = r.adaptive_type or "MAIN"
            type_count[qtype] = type_count.get(qtype, 0) + 1
            if r.overall_score is not None:
                type_map.setdefault(qtype, []).append(r.overall_score)

        items = []
        for qtype, count in type_count.items():
            scores = type_map.get(qtype, [])
            avg = round(sum(scores) / len(scores), 1) if scores else None
            items.append(QuestionTypeItem(type=qtype, count=count, average_score=avg))

        return items

    def get_adaptive_stats(self, user_id: str) -> AdaptiveAnalytics:
        """Calculate statistics for adaptive follow-up and counter questions."""
        sq_rows = (
            self.db.query(
                InterviewSessionQuestion.question_depth,
                InterviewSessionQuestion.adaptive_type,
                InterviewAnswerEvaluation.overall_score,
            )
            .join(InterviewSession, InterviewSessionQuestion.session_id == InterviewSession.id)
            .outerjoin(InterviewAnswer, InterviewAnswer.session_question_id == InterviewSessionQuestion.id)
            .outerjoin(InterviewAnswerEvaluation, InterviewAnswerEvaluation.answer_id == InterviewAnswer.id)
            .filter(InterviewSession.user_id == user_id)
            .all()
        )

        main_q = 0
        followup_q = 0
        counter_q = 0
        followup_scores = []
        counter_scores = []

        for r in sq_rows:
            depth = r.question_depth or 0
            atype = r.adaptive_type or "MAIN"

            if depth == 0 and atype == "MAIN":
                main_q += 1
            elif depth == 1 or atype == "FOLLOW_UP":
                followup_q += 1
                if r.overall_score is not None:
                    followup_scores.append(r.overall_score)
            elif depth == 2 or atype == "COUNTER":
                counter_q += 1
                if r.overall_score is not None:
                    counter_scores.append(r.overall_score)

        avg_followup = round(sum(followup_scores) / len(followup_scores), 1) if followup_scores else None
        avg_counter = round(sum(counter_scores) / len(counter_scores), 1) if counter_scores else None

        follow_up_trigger_rate = round((followup_q / main_q) * 100.0, 1) if main_q > 0 else 0.0
        counter_trigger_rate = round((counter_q / followup_q) * 100.0, 1) if followup_q > 0 else 0.0

        return AdaptiveAnalytics(
            main_questions=main_q,
            follow_up_questions=followup_q,
            counter_questions=counter_q,
            average_follow_up_score=avg_followup,
            average_counter_score=avg_counter,
            follow_up_trigger_rate=follow_up_trigger_rate,
            counter_trigger_rate=counter_trigger_rate,
        )

    def get_weak_areas(self, user_id: str) -> List[WeakArea]:
        """Identify weak evaluation dimensions based on score threshold and sample size."""
        skills = self.get_skill_analysis(user_id)
        evals = (
            self._get_user_evaluations_query(user_id)
            .order_by(desc(InterviewAnswerEvaluation.created_at))
            .all()
        )

        weak_areas = []
        dimensions = ["content", "clarity", "depth", "reasoning", "balance", "communication"]

        for dim in dimensions:
            item: SkillItem = getattr(skills, dim)
            if item.average_score is not None and item.evaluated_answers_count >= MINIMUM_SAMPLE_SIZE:
                if item.average_score < ANALYTICS_WEAK_SCORE_THRESHOLD:
                    recent = getattr(evals[0], f"{dim}_score") if evals else None
                    recommendations = {
                        "content": "Focus on grounding arguments in concrete facts, acts, and policy data.",
                        "clarity": "Structure responses with clear intro, numbered points, and conclusion.",
                        "depth": "Elaborate on root causes, multi-stakeholder impacts, and historical context.",
                        "reasoning": "Strengthen cause-and-effect logical arguments and administrative rationale.",
                        "balance": "Acknowledge counter-perspectives, constitutional principles, and pragmatic trade-offs.",
                        "communication": "Maintain articulate tone, precise vocabulary, and steady pacing.",
                    }
                    weak_areas.append(
                        WeakArea(
                            dimension=dim.capitalize(),
                            average_score=item.average_score,
                            sample_size=item.evaluated_answers_count,
                            recent_score=recent,
                            improvement_needed=recommendations.get(dim, "Targeted practice required."),
                        )
                    )

        weak_areas.sort(key=lambda x: x.average_score)
        return weak_areas

    def get_strong_areas(self, user_id: str) -> List[StrongArea]:
        """Identify strong evaluation dimensions based on score threshold and sample size."""
        skills = self.get_skill_analysis(user_id)
        strong_areas = []
        dimensions = ["content", "clarity", "depth", "reasoning", "balance", "communication"]

        for dim in dimensions:
            item: SkillItem = getattr(skills, dim)
            if item.average_score is not None and item.evaluated_answers_count >= MINIMUM_SAMPLE_SIZE:
                if item.average_score >= ANALYTICS_STRONG_SCORE_THRESHOLD:
                    strong_areas.append(
                        StrongArea(
                            dimension=dim.capitalize(),
                            average_score=item.average_score,
                            sample_size=item.evaluated_answers_count,
                        )
                    )

        strong_areas.sort(key=lambda x: x.average_score, reverse=True)
        return strong_areas

    def get_practice_activity(self, user_id: str, days: int = 30) -> List[ActivityPoint]:
        """Return daily count of answered questions and completed sessions over specified lookback window."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        ans_rows = (
            self._get_user_answers_query(user_id)
            .filter(InterviewAnswer.submitted_at >= cutoff)
            .all()
        )

        sess_rows = (
            self.db.query(InterviewSession)
            .filter(
                InterviewSession.user_id == user_id,
                InterviewSession.status == SessionStatus.COMPLETED.value,
                InterviewSession.completed_at >= cutoff,
            )
            .all()
        )

        activity_map: Dict[str, Dict[str, int]] = {}

        for a in ans_rows:
            if a.submitted_at:
                d_str = a.submitted_at.astimezone(timezone.utc).strftime("%Y-%m-%d")
                activity_map.setdefault(d_str, {"questions": 0, "interviews": 0})
                activity_map[d_str]["questions"] += 1

        for s in sess_rows:
            if s.completed_at:
                d_str = s.completed_at.astimezone(timezone.utc).strftime("%Y-%m-%d")
                activity_map.setdefault(d_str, {"questions": 0, "interviews": 0})
                activity_map[d_str]["interviews"] += 1

        points = [
            ActivityPoint(
                date=d_str,
                questions_answered=data["questions"],
                interviews_completed=data["interviews"],
            )
            for d_str, data in sorted(activity_map.items())
        ]

        return points

    def get_interview_history(
        self,
        user_id: str,
        status: Optional[str] = None,
        interview_type: Optional[str] = None,
        input_mode: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> AnalyticsHistoryResponse:
        """Retrieve paginated user interview history with analytics aggregates."""
        query = self.db.query(InterviewSession).filter(InterviewSession.user_id == user_id)

        if status:
            query = query.filter(InterviewSession.status == status.upper())
        if interview_type:
            query = query.filter(InterviewSession.interview_type == interview_type.upper())
        if input_mode:
            query = query.filter(InterviewSession.input_mode == input_mode.upper())

        total = query.count()
        pages = (total + page_size - 1) // page_size if page_size > 0 else 1

        sessions = (
            query.order_by(desc(InterviewSession.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        items = []
        for s in sessions:
            ans_count = (
                self.db.query(func.count(InterviewAnswer.id))
                .join(InterviewSessionQuestion, InterviewAnswer.session_question_id == InterviewSessionQuestion.id)
                .filter(InterviewSessionQuestion.session_id == s.id)
                .scalar()
                or 0
            )

            eval_stats = (
                self.db.query(
                    func.count(InterviewAnswerEvaluation.id).label("count"),
                    func.avg(InterviewAnswerEvaluation.overall_score).label("avg"),
                )
                .join(InterviewAnswer, InterviewAnswerEvaluation.answer_id == InterviewAnswer.id)
                .join(InterviewSessionQuestion, InterviewAnswer.session_question_id == InterviewSessionQuestion.id)
                .filter(InterviewSessionQuestion.session_id == s.id)
                .first()
            )

            eval_count = eval_stats.count or 0 if eval_stats else 0
            avg_score = round(float(eval_stats.avg), 1) if eval_stats and eval_stats.avg is not None else None

            items.append(
                AnalyticsHistoryItem(
                    session_id=s.id,
                    interview_type=s.interview_type,
                    input_mode=getattr(s, "input_mode", "TEXT") or "TEXT",
                    status=s.status,
                    total_questions=s.total_questions,
                    answered_questions=ans_count,
                    evaluated_answers=eval_count,
                    average_score=avg_score,
                    started_at=s.started_at,
                    completed_at=s.completed_at,
                )
            )

        return AnalyticsHistoryResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    def get_dashboard(self, user_id: str) -> AnalyticsDashboard:
        """Aggregate compact dashboard payload for Progress Page."""
        overview = self.get_overview(user_id)
        skills = self.get_skill_analysis(user_id)
        trends = self.get_score_trend(user_id, period="30d")
        topics = self.get_topic_performance(user_id)
        question_types = self.get_question_type_performance(user_id)
        adaptive = self.get_adaptive_stats(user_id)
        weak_areas = self.get_weak_areas(user_id)
        strong_areas = self.get_strong_areas(user_id)
        activity = self.get_practice_activity(user_id, days=30)
        history = self.get_interview_history(user_id, page=1, page_size=5)

        return AnalyticsDashboard(
            overview=overview,
            skills=skills,
            recent_trend=trends.points,
            topics=topics,
            question_types=question_types,
            adaptive=adaptive,
            weak_areas=weak_areas,
            strong_areas=strong_areas,
            recent_activity=activity,
            recent_interviews=history.items,
        )
