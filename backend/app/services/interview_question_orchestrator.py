import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.user import User
from app.models.question import InterviewQuestion
from app.models.interview import InterviewSession, InterviewType, InterviewSessionQuestion
from app.services.question_generation_service import generate_interview_question
from app.services.personalization_service import generate_personalized_interview_question

from app.services.gemini_service import BaseGeminiService, get_gemini_service

logger = logging.getLogger("interview_orchestrator")


class InterviewQuestionOrchestrator:
    """Orchestrates question selection/generation for an AI interview session reusing existing Phase 1–8 engines."""

    def __init__(self, db: Session, gemini_service: Optional[BaseGeminiService] = None):
        self.db = db
        self.gemini_service = gemini_service or get_gemini_service()

    def get_or_create_next_question(
        self,
        session: InterviewSession,
        user: User,
        include_daf_questions: bool = True,
        include_current_affairs: bool = True,
        include_rag_questions: bool = True,
        difficulty: str = "MODERATE",
        topic: Optional[str] = None,
        category: Optional[str] = None,
    ) -> InterviewQuestion:
        # Collect question_ids already served in this session to prevent repetition
        existing_q_ids = [
            sq.question_id
            for sq in session.session_questions
            if sq.question_id is not None
        ]

        # 1. DAF-Personalized Question Selection / Generation
        if session.interview_type == InterviewType.DAF_INTERVIEW.value or (
            include_daf_questions and (session.current_question_index % 2 == 1)
        ):
            daf_question = self._try_daf_question(user=user, difficulty=difficulty, existing_ids=existing_q_ids)
            if daf_question:
                return daf_question

        # 2. Current Affairs Question Selection
        if session.interview_type == InterviewType.CURRENT_AFFAIRS.value or (
            include_current_affairs and (session.current_question_index % 3 == 0)
        ):
            ca_question = self._try_current_affairs_question(existing_ids=existing_q_ids, category=category)
            if ca_question:
                return ca_question

        # 3. Existing Question Bank Match (Prefer reuse over duplicate generation)
        bank_question = self._try_question_bank(
            existing_ids=existing_q_ids,
            user_id=user.id,
            difficulty=difficulty,
            category=category,
            topic=topic,
        )
        if bank_question:
            return bank_question

        # 4. Fallback RAG-Grounded Question Generation
        rag_question = self._try_rag_grounded_question(
            user=user,
            difficulty=difficulty,
            category=category or "GOVERNANCE",
            topic=topic or "Public Administration & Governance",
        )
        if rag_question:
            return rag_question

        # 5. Last Resort General UPSC Question
        return self._create_fallback_upsc_question(user=user, difficulty=difficulty, topic=topic, category=category)

    def _try_daf_question(self, user: User, difficulty: str, existing_ids: List[str]) -> Optional[InterviewQuestion]:
        sources = ["EDUCATION", "HOMETOWN", "OPTIONAL_SUBJECT", "HOBBY", "GENERAL_DAF"]
        for src in sources:
            try:
                res = generate_personalized_interview_question(
                    db=self.db,
                    current_user=user,
                    source=src,
                    difficulty=difficulty,
                )
                q_id = res.get("id")
                if q_id and q_id not in existing_ids:
                    return self.db.query(InterviewQuestion).filter(InterviewQuestion.id == q_id).first()
            except Exception as e:
                logger.debug(f"DAF question generation skipped for source {src}: {e}")
        return None

    def _try_current_affairs_question(self, existing_ids: List[str], category: Optional[str]) -> Optional[InterviewQuestion]:
        query = self.db.query(InterviewQuestion).filter(
            InterviewQuestion.current_affair_id.isnot(None)
        )
        if category:
            query = query.filter(InterviewQuestion.category == category)
        if existing_ids:
            query = query.filter(InterviewQuestion.id.notin_(existing_ids))
        
        return query.order_by(InterviewQuestion.created_at.desc()).first()

    def _try_question_bank(
        self,
        existing_ids: List[str],
        user_id: str,
        difficulty: str,
        category: Optional[str],
        topic: Optional[str],
    ) -> Optional[InterviewQuestion]:
        query = self.db.query(InterviewQuestion).filter(
            or_(InterviewQuestion.user_id == user_id, InterviewQuestion.user_id.is_(None))
        )
        if existing_ids:
            query = query.filter(InterviewQuestion.id.notin_(existing_ids))
        if difficulty:
            query = query.filter(InterviewQuestion.difficulty == difficulty)
        if category:
            query = query.filter(InterviewQuestion.category == category)
        if topic:
            query = query.filter(InterviewQuestion.topic.ilike(f"%{topic}%"))

        return query.order_by(InterviewQuestion.created_at.desc()).first()

    def _try_rag_grounded_question(
        self, user: User, difficulty: str, category: str, topic: str
    ) -> Optional[InterviewQuestion]:
        try:
            res = generate_interview_question(
                db=self.db,
                current_user_id=user.id,
                topic=topic,
                subject="General Studies",
                category=category,
                difficulty=difficulty,
            )
            q_id = res.get("id")
            if q_id:
                return self.db.query(InterviewQuestion).filter(InterviewQuestion.id == q_id).first()
        except Exception as e:
            logger.warning(f"RAG grounded question generation fallback error: {e}")
        return None

    def _create_fallback_upsc_question(
        self, user: User, difficulty: str, topic: Optional[str], category: Optional[str]
    ) -> InterviewQuestion:
        # Retrieve a fallback question from the database instead of hardcoding
        query = self.db.query(InterviewQuestion).filter(
            InterviewQuestion.status == "ACTIVE",
            InterviewQuestion.question_type == "MAIN"
        )
        if topic:
            query = query.filter(InterviewQuestion.topic == topic)
        if category:
            query = query.filter(InterviewQuestion.category == category)
            
        fallback_q = query.first()
        if fallback_q:
            return fallback_q
            
        # If absolutely no questions exist in DB (unseeded), return the first available active question
        fallback_q = self.db.query(InterviewQuestion).filter(InterviewQuestion.status == "ACTIVE").first()
        if fallback_q:
            return fallback_q
            
        # Failsafe if DB is completely empty (should never happen in production with seeds)
        raise ValueError("No active questions available in the Question Bank database.")
