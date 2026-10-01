"""
Context Builder for AI Preparation Coach.

Assembles privacy-isolated, bounded candidate context for recommendation engine
by calling existing AnalyticsService methods and fetching DAF, Resources, and Current Affairs data.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.profile import UserProfile
from app.models.resource import Resource
from app.models.current_affair import CurrentAffair
from app.services.analytics_service import AnalyticsService


class CoachContextBuilder:
    """Assembles privacy-isolated, bounded candidate context for recommendation engine."""

    @classmethod
    def build_candidate_context(cls, db: Session, user_id: str) -> Dict[str, Any]:
        """Collect bounded analytics, profile metadata, resource counts, and current affairs."""
        user = db.query(User).filter(User.id == user_id).first()
        user_name = user.full_name if user else "Aspirant"

        # 1. Profile / DAF metadata
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        daf_info = {}
        if profile:
            education_bg = ""
            if profile.education_data and isinstance(profile.education_data, dict):
                education_bg = profile.education_data.get("graduation_degree") or profile.education_data.get("subject") or ""

            optional_subj = ""
            if profile.upsc_journey_data and isinstance(profile.upsc_journey_data, dict):
                optional_subj = profile.upsc_journey_data.get("optional_subject") or ""

            hobbies_str = ""
            if profile.interests and isinstance(profile.interests, dict):
                hobbies_str = profile.interests.get("hobbies") or ""

            daf_info = {
                "education_background": education_bg,
                "optional_subject": optional_subj,
                "home_state": profile.home_state,
                "home_district": profile.district,
                "hobbies": hobbies_str,
                "profile_completion": profile.profile_completion,
            }

        # 2. Analytics metrics via existing AnalyticsService
        analytics_service = AnalyticsService(db)
        overview = analytics_service.get_overview(user_id)
        skills = analytics_service.get_skill_analysis(user_id)
        topics = analytics_service.get_topic_performance(user_id)
        weak_areas = analytics_service.get_weak_areas(user_id)
        strong_areas = analytics_service.get_strong_areas(user_id)
        adaptive = analytics_service.get_adaptive_stats(user_id)

        # 3. Available resources in database
        db_resources = (
            db.query(Resource.id, Resource.title, Resource.category, Resource.subject)
            .limit(5)
            .all()
        )
        resources_info = [
            {"id": r.id, "title": r.title, "category": r.category, "subject": r.subject}
            for r in db_resources
        ]

        # 4. Active Current Affairs topics in database
        db_ca = (
            db.query(CurrentAffair.id, CurrentAffair.title, CurrentAffair.category)
            .order_by(CurrentAffair.created_at.desc())
            .limit(5)
            .all()
        )
        ca_info = [
            {"id": a.id, "title": a.title, "category": a.category}
            for a in db_ca
        ]

        has_evaluations = (overview.total_evaluated_answers > 0)

        return {
            "user_id": user_id,
            "candidate_name": user_name,
            "has_evaluations": has_evaluations,
            "daf": daf_info,
            "overview": overview.model_dump(),
            "skills": skills.model_dump(),
            "topics": [t.model_dump() for t in topics[:5]],
            "weak_areas": [w.model_dump() for w in weak_areas],
            "strong_areas": [s.model_dump() for s in strong_areas],
            "adaptive": adaptive.model_dump(),
            "available_resources": resources_info,
            "recent_current_affairs": ca_info,
        }
