import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.interview import InterviewSession, QuestionSessionStatus
from app.models.evaluation import InterviewAnswerEvaluation
from app.schemas.interview import (
    InterviewStartRequest,
    AnswerSubmitRequest,
    InterviewSessionResponse,
    SessionQuestionItem,
    AnswerSubmitResponse,
    NextQuestionResponse,
    InterviewCompleteResponse,
    InterviewHistoryResponse,
    AdaptiveMetadata,
)
from app.schemas.evaluation import EvaluationResponse, EvaluationDimension
from app.services.interview_session_service import InterviewSessionService
from app.services.answer_evaluation_service import AnswerEvaluationService

logger = logging.getLogger("interview_router")

router = APIRouter(
    prefix="/interview",
    tags=["AI Interview Session Engine"],
)


def format_session_response(session: InterviewSession) -> InterviewSessionResponse:
    curr_sq = None
    for sq in session.session_questions:
        if sq.sequence_number == session.current_question_index:
            curr_sq = sq
            break

    curr_q_item = None
    if curr_sq and curr_sq.question:
        q = curr_sq.question
        curr_q_item = SessionQuestionItem(
            id=curr_sq.id,
            sequence_number=curr_sq.sequence_number,
            question_status=curr_sq.question_status,
            text=q.question_text,
            type=q.question_type,
            difficulty=q.difficulty,
            category=q.category,
            topic=q.topic,
            is_personalized=q.is_personalized,
            personalization_source=q.personalization_source,
            personalization_label=q.personalization_label,
            explanation=q.explanation,
            why_this_matters=q.why_this_matters,
        )

    all_questions = []
    for sq in session.session_questions:
        if sq.question:
            q = sq.question
            all_questions.append(
                SessionQuestionItem(
                    id=sq.id,
                    sequence_number=sq.sequence_number,
                    question_status=sq.question_status,
                    text=q.question_text,
                    type=q.question_type,
                    difficulty=q.difficulty,
                    category=q.category,
                    topic=q.topic,
                    is_personalized=q.is_personalized,
                    personalization_source=q.personalization_source,
                    personalization_label=q.personalization_label,
                    explanation=q.explanation,
                    why_this_matters=q.why_this_matters,
                    question_depth=sq.question_depth or 0,
                    parent_session_question_id=sq.parent_session_question_id,
                    parent_answer_id=sq.parent_answer_id,
                )
            )

    return InterviewSessionResponse(
        session_id=session.id,
        status=session.status,
        interview_type=session.interview_type,
        total_questions=session.total_questions,
        current_question_index=session.current_question_index,
        input_mode=getattr(session, "input_mode", "TEXT") or "TEXT",
        language=getattr(session, "language", "en-IN") or "en-IN",
        current_question=curr_q_item,
        questions=all_questions,
        started_at=session.started_at,
        completed_at=session.completed_at,
        created_at=session.created_at,
    )


@router.post("/start", response_model=InterviewSessionResponse, status_code=status.HTTP_201_CREATED)
def start_interview(
    req: InterviewStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start a new AI UPSC Interview Session with requested configuration."""
    service = InterviewSessionService(db)
    session = service.start_interview(user=current_user, config=req.model_dump())
    return format_session_response(session)


@router.get("/history", response_model=InterviewHistoryResponse)
def get_interview_history(
    status: Optional[str] = Query(None, description="Filter by session status (CREATED, IN_PROGRESS, COMPLETED, ABANDONED)"),
    interview_type: Optional[str] = Query(None, description="Filter by interview type"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve authenticated user's interview sessions history."""
    service = InterviewSessionService(db)
    history_data = service.get_interview_history(
        user_id=current_user.id,
        session_status=status,
        interview_type=interview_type,
        page=page,
        page_size=page_size,
    )
    return InterviewHistoryResponse(**history_data)


@router.get("/{session_id}", response_model=InterviewSessionResponse)
def get_interview_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve detailed state of an active or completed interview session."""
    service = InterviewSessionService(db)
    session = service.get_session(session_id=session_id, user_id=current_user.id)
    return format_session_response(session)


@router.post("/{session_id}/answer", response_model=AnswerSubmitResponse)
def submit_interview_answer(
    session_id: str,
    req: AnswerSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit answer text and duration for the current session question."""
    service = InterviewSessionService(db)
    result = service.submit_answer(
        session_id=session_id,
        user_id=current_user.id,
        answer_text=req.answer_text,
        duration_seconds=req.answer_duration_seconds,
    )
    return AnswerSubmitResponse(**result)


@router.post("/{session_id}/next-question", response_model=NextQuestionResponse)
def get_next_interview_question(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Progress session sequence and receive the next served question (adaptive or main)."""
    service = InterviewSessionService(db)
    next_sq = service.get_next_question(session_id=session_id, user_id=current_user.id)
    session = service.get_session(session_id=session_id, user_id=current_user.id)

    adaptive_count = sum(1 for sq in session.session_questions if sq.question_depth > 0)
    total_served = len(session.session_questions)

    q = next_sq.question
    q_item = SessionQuestionItem(
        id=next_sq.id,
        sequence_number=next_sq.sequence_number,
        question_status=next_sq.question_status,
        text=q.question_text if q else "General UPSC Interview Question",
        type="MAIN" if next_sq.question_depth == 0 else (q.question_type if q else (next_sq.adaptive_type or "MAIN")),
        difficulty=q.difficulty if q else "MODERATE",
        category=q.category if q else None,
        topic=q.topic if q else None,
        is_personalized=q.is_personalized if q else False,
        personalization_source=q.personalization_source if q else None,
        personalization_label=q.personalization_label if q else None,
        explanation=q.explanation if q else None,
        why_this_matters=q.why_this_matters if q else None,
        question_depth=next_sq.question_depth or 0,
        parent_session_question_id=next_sq.parent_session_question_id,
        parent_answer_id=next_sq.parent_answer_id,
    )

    adaptive_meta = AdaptiveMetadata(
        is_adaptive=next_sq.question_depth > 0,
        parent_question_id=next_sq.parent_session_question_id,
        parent_answer_id=next_sq.parent_answer_id,
        depth=next_sq.question_depth or 0,
        adaptive_type=next_sq.adaptive_type or "MAIN",
        generated_reason=next_sq.generated_reason,
    )

    all_questions = []
    for sq in session.session_questions:
        if sq.question:
            q_obj = sq.question
            all_questions.append(
                SessionQuestionItem(
                    id=sq.id,
                    sequence_number=sq.sequence_number,
                    question_status=sq.question_status,
                    text=q_obj.question_text,
                    type=q_obj.question_type,
                    difficulty=q_obj.difficulty,
                    category=q_obj.category,
                    topic=q_obj.topic,
                    is_personalized=q_obj.is_personalized,
                    personalization_source=q_obj.personalization_source,
                    personalization_label=q_obj.personalization_label,
                    explanation=q_obj.explanation,
                    why_this_matters=q_obj.why_this_matters,
                    question_depth=sq.question_depth or 0,
                    parent_session_question_id=sq.parent_session_question_id,
                    parent_answer_id=sq.parent_answer_id,
                )
            )

    return NextQuestionResponse(
        session_id=session.id,
        question=q_item,
        progress={
            "current": session.current_question_index,
            "total": session.total_questions,
            "total_main_questions": session.total_questions,
            "served_questions": total_served,
            "adaptive_questions": adaptive_count,
        },
        adaptive=adaptive_meta,
        questions=all_questions,
    )


@router.post("/{session_id}/skip")
def skip_interview_question(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark current session question as SKIPPED."""
    service = InterviewSessionService(db)
    return service.skip_question(session_id=session_id, user_id=current_user.id)


@router.get("/{session_id}/report")
def get_interview_session_report(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve comprehensive session performance report."""
    service = AnswerEvaluationService(db)
    return service.generate_session_report(session_id=session_id, user_id=current_user.id)


@router.post("/{session_id}/complete", response_model=InterviewCompleteResponse)
def complete_interview(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark interview session as COMPLETED."""
    service = InterviewSessionService(db)
    session = service.complete_interview(session_id=session_id, user_id=current_user.id)

    answered_count = sum(
        1 for sq in session.session_questions if sq.question_status == QuestionSessionStatus.ANSWERED.value
    )

    return InterviewCompleteResponse(
        session_id=session.id,
        status=session.status,
        completed_at=session.completed_at,
        total_questions=session.total_questions,
        answered_questions=answered_count,
    )


def format_evaluation_response(eval_obj: InterviewAnswerEvaluation) -> EvaluationResponse:
    return EvaluationResponse(
        id=eval_obj.id,
        answer_id=eval_obj.answer_id,
        content=EvaluationDimension(score=eval_obj.content_score, feedback=eval_obj.content_feedback),
        clarity=EvaluationDimension(score=eval_obj.clarity_score, feedback=eval_obj.clarity_feedback),
        depth=EvaluationDimension(score=eval_obj.depth_score, feedback=eval_obj.depth_feedback),
        reasoning=EvaluationDimension(score=eval_obj.reasoning_score, feedback=eval_obj.reasoning_feedback),
        balance=EvaluationDimension(score=eval_obj.balance_score, feedback=eval_obj.balance_feedback),
        communication=EvaluationDimension(score=eval_obj.communication_score, feedback=eval_obj.communication_feedback),
        overall_score=eval_obj.overall_score,
        overall_feedback=eval_obj.overall_feedback,
        strengths=eval_obj.strengths or [],
        areas_to_improve=eval_obj.areas_to_improve or [],
        suggested_answer=eval_obj.suggested_answer,
        created_at=eval_obj.created_at,
        updated_at=eval_obj.updated_at,
    )


@router.post("/answers/{answer_id}/evaluate", response_model=EvaluationResponse)
def evaluate_interview_answer(
    answer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Evaluate a candidate's answer using AI evaluation service and store backend score."""
    service = AnswerEvaluationService(db)
    eval_obj = service.evaluate_answer(answer_id=answer_id, user_id=current_user.id)
    return format_evaluation_response(eval_obj)


@router.get("/answers/{answer_id}/evaluation", response_model=EvaluationResponse)
def get_interview_answer_evaluation(
    answer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve existing evaluation for an answer."""
    service = AnswerEvaluationService(db)
    eval_obj = service.get_evaluation(answer_id=answer_id, user_id=current_user.id)
    return format_evaluation_response(eval_obj)

