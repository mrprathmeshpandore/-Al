import logging
import math
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.user import User
from app.models.question import InterviewQuestion
from app.models.interview import (
    InterviewSession,
    InterviewSessionQuestion,
    InterviewAnswer,
    SessionStatus,
    InterviewType,
    QuestionSessionStatus,
)
from app.services.interview_question_orchestrator import InterviewQuestionOrchestrator
from app.services.followup_engine import FollowupEngine
from app.services.counter_question_engine import CounterQuestionEngine

MAX_ADAPTIVE_DEPTH = 2

logger = logging.getLogger("interview_session_service")

VALID_INTERVIEW_TYPES = [t.value for t in InterviewType]


class InterviewSessionService:
    """Manages AI interview session creation, progression, answer storage, state machine, and history."""

    def __init__(self, db: Session, gemini_service: Optional[BaseGeminiService] = None):
        self.db = db
        self.gemini_service = gemini_service
        self.orchestrator = InterviewQuestionOrchestrator(db, gemini_service=gemini_service)

    def start_interview(self, user: User, config: Dict[str, Any]) -> InterviewSession:
        raw_type = str(config.get("interview_type", InterviewType.FULL_INTERVIEW.value)).upper()
        if raw_type not in VALID_INTERVIEW_TYPES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unsupported interview_type '{raw_type}'. Supported types: {VALID_INTERVIEW_TYPES}",
            )

        total_questions = config.get("total_questions", 10)
        if not isinstance(total_questions, int) or total_questions < 1 or total_questions > 20:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="total_questions must be an integer between 1 and 20.",
            )

        difficulty = str(config.get("difficulty", "MODERATE")).upper()
        if difficulty not in ["EASY", "MODERATE", "CHALLENGING", "HARD"]:
            difficulty = "MODERATE"

        # Create InterviewSession
        now = datetime.now(timezone.utc)
        session = InterviewSession(
            user_id=user.id,
            status=SessionStatus.IN_PROGRESS.value,
            interview_type=raw_type,
            total_questions=total_questions,
            current_question_index=1,
            include_adaptive=config.get("include_adaptive", True),
            input_mode=str(config.get("input_mode", "TEXT")).upper(),
            language=str(config.get("language", "en-IN")),
            started_at=now,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        # Select/Generate Question 1
        q1 = self.orchestrator.get_or_create_next_question(
            session=session,
            user=user,
            include_daf_questions=config.get("include_daf_questions", True),
            include_current_affairs=config.get("include_current_affairs", True),
            include_rag_questions=config.get("include_rag_questions", True),
            difficulty=difficulty,
            topic=config.get("topic"),
            category=config.get("category"),
        )

        sq1 = InterviewSessionQuestion(
            session_id=session.id,
            question_id=q1.id,
            sequence_number=1,
            question_status=QuestionSessionStatus.ASKED.value,
            presented_at=now,
        )
        self.db.add(sq1)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session(self, session_id: str, user_id: str) -> InterviewSession:
        session = (
            self.db.query(InterviewSession)
            .filter(InterviewSession.id == session_id, InterviewSession.user_id == user_id)
            .first()
        )
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found or access denied.",
            )
        return session

    def submit_answer(
        self, session_id: str, user_id: str, answer_text: str, duration_seconds: int
    ) -> Dict[str, Any]:
        session = self.get_session(session_id, user_id)

        if session.status != SessionStatus.IN_PROGRESS.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot submit answer. Session is currently in '{session.status}' state.",
            )

        clean_text = (answer_text or "").strip()
        if not clean_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Answer text must not be empty.",
            )

        if duration_seconds < 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Answer duration seconds cannot be negative.",
            )

        # Find active session question for current sequence number
        sq = (
            self.db.query(InterviewSessionQuestion)
            .filter(
                InterviewSessionQuestion.session_id == session.id,
                InterviewSessionQuestion.sequence_number == session.current_question_index,
            )
            .first()
        )

        if not sq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Current question for sequence index {session.current_question_index} not found.",
            )

        if sq.question_status == QuestionSessionStatus.ANSWERED.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Question at index {session.current_question_index} has already been answered.",
            )

        now = datetime.now(timezone.utc)
        answer = InterviewAnswer(
            session_question_id=sq.id,
            answer_text=clean_text,
            submitted_at=now,
            answer_duration_seconds=duration_seconds,
        )
        self.db.add(answer)

        sq.question_status = QuestionSessionStatus.ANSWERED.value
        sq.answered_at = now
        self.db.commit()
        self.db.refresh(answer)

        next_action = (
            "COMPLETE_INTERVIEW"
            if session.current_question_index >= session.total_questions
            else "NEXT_QUESTION"
        )

        return {
            "answer_id": answer.id,
            "session_question_id": sq.id,
            "submitted_at": answer.submitted_at,
            "next_action": next_action,
        }

    def get_next_question(
        self, session_id: str, user_id: str, config: Optional[Dict[str, Any]] = None
    ) -> InterviewSessionQuestion:
        session = self.get_session(session_id, user_id)
        user = self.db.query(User).filter(User.id == user_id).first()

        if session.status != SessionStatus.IN_PROGRESS.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot fetch next question. Session is in '{session.status}' state.",
            )

        # Check current session question state
        curr_sq = (
            self.db.query(InterviewSessionQuestion)
            .filter(
                InterviewSessionQuestion.session_id == session.id,
                InterviewSessionQuestion.sequence_number == session.current_question_index,
            )
            .first()
        )

        # IDEMPOTENCY: If current question was generated via next-question (index > 1) and is still ASKED, return it
        if curr_sq and curr_sq.question_status == QuestionSessionStatus.ASKED.value and session.current_question_index > 1:
            return curr_sq

        if not curr_sq or curr_sq.question_status != QuestionSessionStatus.ANSWERED.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Current question at index {session.current_question_index} must be answered before moving to the next question.",
            )

        # IDEMPOTENCY CHECK: If next question at sequence index (current_index + 1) already exists, return it
        target_seq = session.current_question_index + 1
        existing_next = (
            self.db.query(InterviewSessionQuestion)
            .filter(
                InterviewSessionQuestion.session_id == session.id,
                InterviewSessionQuestion.sequence_number == target_seq,
            )
            .first()
        )
        if existing_next:
            session.current_question_index = target_seq
            self.db.commit()
            return existing_next

        # Retrieve candidate's answer for current question
        ans = (
            self.db.query(InterviewAnswer)
            .filter(InterviewAnswer.session_question_id == curr_sq.id)
            .first()
        )

        # Check total questions limit if non-adaptive
        main_q_count = (
            self.db.query(InterviewSessionQuestion)
            .filter(
                InterviewSessionQuestion.session_id == session.id,
                InterviewSessionQuestion.question_depth == 0,
            )
            .count()
        )

        config = config or {}
        should_adaptive = config.get("include_adaptive", getattr(session, "include_adaptive", True))

        adaptive_q = None
        adaptive_type = "MAIN"
        generated_reason = None

        # Attempt Adaptive Questioning if enabled, depth < MAX_ADAPTIVE_DEPTH and answer is available
        if should_adaptive and ans and curr_sq.question_depth < MAX_ADAPTIVE_DEPTH:
            if curr_sq.question_depth == 0:
                # Try FollowupEngine
                followup_engine = FollowupEngine(self.db, gemini_service=self.gemini_service)
                should_f, f_question, f_reason = followup_engine.evaluate_and_generate_followup(
                    session_question=curr_sq,
                    answer=ans,
                    user=user,
                )
                if should_f and f_question:
                    adaptive_q = f_question
                    adaptive_type = f_question.question_type or "FOLLOW_UP"
                    generated_reason = f_reason
            elif curr_sq.question_depth == 1:
                # Try CounterQuestionEngine
                counter_engine = CounterQuestionEngine(self.db, gemini_service=self.gemini_service)
                should_c, c_question, c_reason = counter_engine.evaluate_and_generate_counter(
                    session_question=curr_sq,
                    answer=ans,
                    user=user,
                )
                if should_c and c_question:
                    adaptive_q = c_question
                    adaptive_type = c_question.question_type or "COUNTER"
                    generated_reason = c_reason

        now = datetime.now(timezone.utc)
        if adaptive_q:
            session.current_question_index += 1
            next_sq = InterviewSessionQuestion(
                session_id=session.id,
                question_id=adaptive_q.id,
                sequence_number=session.current_question_index,
                question_status=QuestionSessionStatus.ASKED.value,
                parent_session_question_id=curr_sq.id,
                parent_answer_id=ans.id if ans else None,
                question_depth=curr_sq.question_depth + 1,
                generated_reason=generated_reason,
                adaptive_type=adaptive_type,
                presented_at=now,
            )
            self.db.add(next_sq)
            self.db.commit()
            self.db.refresh(next_sq)
            return next_sq

        # If no adaptive question generated, check if main questions limit reached
        if main_q_count >= session.total_questions:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"All {session.total_questions} main questions for this session have been completed.",
            )

        # Fallback to Next MAIN Question from Orchestrator
        session.current_question_index += 1
        config = config or {}
        next_main_q = self.orchestrator.get_or_create_next_question(
            session=session,
            user=user,
            include_daf_questions=config.get("include_daf_questions", True),
            include_current_affairs=config.get("include_current_affairs", True),
            include_rag_questions=config.get("include_rag_questions", True),
            difficulty=config.get("difficulty", "MODERATE"),
            topic=config.get("topic"),
            category=config.get("category"),
        )

        next_sq = InterviewSessionQuestion(
            session_id=session.id,
            question_id=next_main_q.id,
            sequence_number=session.current_question_index,
            question_status=QuestionSessionStatus.ASKED.value,
            parent_session_question_id=None,
            parent_answer_id=None,
            question_depth=0,
            generated_reason=None,
            adaptive_type="MAIN",
            presented_at=now,
        )
        self.db.add(next_sq)
        self.db.commit()
        self.db.refresh(next_sq)
        return next_sq

    def complete_interview(self, session_id: str, user_id: str) -> InterviewSession:
        session = self.get_session(session_id, user_id)

        if session.status == SessionStatus.COMPLETED.value:
            return session

        if session.status == SessionStatus.ABANDONED.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Abandoned session cannot be marked as completed.",
            )

        session.status = SessionStatus.COMPLETED.value
        session.completed_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_interview_history(
        self,
        user_id: str,
        session_status: Optional[str] = None,
        interview_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Dict[str, Any]:
        query = self.db.query(InterviewSession).filter(InterviewSession.user_id == user_id)

        if session_status:
            query = query.filter(InterviewSession.status == session_status.strip().upper())

        if interview_type:
            query = query.filter(InterviewSession.interview_type == interview_type.strip().upper())

        total = query.count()
        pages = math.ceil(total / page_size) if total > 0 else 1
        offset = (page - 1) * page_size

        sessions = (
            query.order_by(InterviewSession.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        history_items = []
        for s in sessions:
            answered_count = (
                self.db.query(InterviewSessionQuestion)
                .filter(
                    InterviewSessionQuestion.session_id == s.id,
                    InterviewSessionQuestion.question_status == QuestionSessionStatus.ANSWERED.value,
                )
                .count()
            )
            history_items.append({
                "session_id": s.id,
                "interview_type": s.interview_type,
                "status": s.status,
                "total_questions": s.total_questions,
                "answered_questions": answered_count,
                "started_at": s.started_at,
                "completed_at": s.completed_at,
                "created_at": s.created_at,
            })

        return {
            "items": history_items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages,
        }
