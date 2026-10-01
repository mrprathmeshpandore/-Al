import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.question import (
    QuestionGenerateRequest,
    PersonalizedQuestionGenerateRequest,
    QuestionResponse,
    QuestionListResponse,
)
from app.services.question_generation_service import (
    generate_interview_question,
    list_user_questions,
    get_user_question_by_id,
    delete_user_question_by_id,
)
from app.services.personalization_service import generate_personalized_interview_question

logger = logging.getLogger("questions_router")

router = APIRouter(
    prefix="/questions",
    tags=["UPSC Interview Question Generation"],
)


@router.post(
    "/generate",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Grounded UPSC Interview Practice Question",
    description="Retrieves relevant knowledge chunks for a given UPSC topic, generates an interview practice question using Gemini, validates question structure and terminology, and persists the question and citation sources.",
)
def generate_question(
    payload: QuestionGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    POST /api/questions/generate
    Authenticates user, retrieves RAG knowledge, generates interview practice question, and stores question in database.
    """
    try:
        response_data = generate_interview_question(
            topic=payload.topic,
            current_user_id=current_user.id,
            db=db,
            subject=payload.subject,
            category=payload.category,
            difficulty=payload.difficulty,
            question_type=payload.question_type,
            top_k=payload.top_k,
        )
        return response_data
    except Exception as e:
        logger.error(f"Error in generate_question endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating interview practice question."
        )


@router.post(
    "/generate-personalized",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate DAF-Personalized UPSC Interview Practice Question",
    description="Formats user DAF profile background into structured context, retrieves RAG knowledge, generates a personalized interview practice question using Gemini, validates question structure, and persists question and citations.",
)
def generate_personalized_question(
    payload: PersonalizedQuestionGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    POST /api/questions/generate-personalized
    Authenticates user, extracts DAF context based on source, retrieves RAG knowledge, generates personalized question, and persists.
    """
    try:
        response_data = generate_personalized_interview_question(
            source=payload.source,
            current_user=current_user,
            db=db,
            difficulty=payload.difficulty,
            question_type=payload.question_type,
            top_k=payload.top_k,
        )
        return response_data
    except Exception as e:
        logger.error(f"Error in generate_personalized_question endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating personalized interview practice question."
        )


@router.get(
    "",
    response_model=QuestionListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Authenticated User's Practice Questions",
    description="Returns a paginated list of generated interview practice questions for the authenticated user with optional subject, topic, difficulty, question type, and personalization filters.",
)
def list_questions(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=50, description="Page size limit"),
    subject: Optional[str] = Query(default=None, description="Filter by subject area"),
    topic: Optional[str] = Query(default=None, description="Filter by topic keyword"),
    category: Optional[str] = Query(default=None, description="Filter by category"),
    difficulty: Optional[str] = Query(default=None, description="Filter by difficulty (EASY, MODERATE, HARD)"),
    question_type: Optional[str] = Query(default=None, description="Filter by question type (MAIN, FOLLOW_UP, COUNTER, ETHICAL, SCENARIO)"),
    is_personalized: Optional[bool] = Query(default=None, description="Filter by personalization status"),
    personalization_source: Optional[str] = Query(default=None, description="Filter by personalization source"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    GET /api/questions
    Lists authenticated user's practice questions with pagination and filtering.
    """
    return list_user_questions(
        user_id=current_user.id,
        db=db,
        page=page,
        page_size=page_size,
        subject=subject,
        topic=topic,
        category=category,
        difficulty=difficulty,
        question_type=question_type,
        is_personalized=is_personalized,
        personalization_source=personalization_source,
    )


@router.get(
    "/{question_id}",
    response_model=QuestionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Single Interview Question Details",
    description="Retrieves a single interview practice question and its backend-verified citation sources by ID.",
)
def get_question_detail(
    question_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    GET /api/questions/{question_id}
    Retrieves single practice question enforcing user isolation.
    """
    data = get_user_question_by_id(question_id=question_id, user_id=current_user.id, db=db)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found or access denied."
        )
    return data


@router.delete(
    "/{question_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Interview Practice Question",
    description="Deletes an interview practice question by ID for the authenticated user.",
)
def delete_question(
    question_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    DELETE /api/questions/{question_id}
    Deletes single practice question enforcing user isolation.
    """
    success = delete_user_question_by_id(question_id=question_id, user_id=current_user.id, db=db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found or access denied."
        )
    return {"message": "Question deleted successfully", "id": question_id}
