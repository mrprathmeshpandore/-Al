import logging
import math
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.constants.current_affairs import VALID_CATEGORIES, CurrentAffairCategory
from app.models.current_affair import CurrentAffair
from app.models.question import InterviewQuestion
from app.schemas.current_affairs import (
    CurrentAffairResponse,
    CurrentAffairListResponse,
    CategoryListResponse,
    CategoryItem,
    TopicListResponse,
    PotentialQuestionResponse,
)
from app.services.current_affairs.ingestion_service import CurrentAffairsIngestionService

logger = logging.getLogger("current_affairs_router")

router = APIRouter(
    prefix="/current-affairs",
    tags=["Current Affairs"],
)


def format_category_label(cat_str: str) -> str:
    labels = {
        "NATIONAL": "National",
        "INTERNATIONAL": "International",
        "ECONOMY": "Economy",
        "GOVERNANCE": "Governance",
        "POLITY": "Polity",
        "ENVIRONMENT": "Environment",
        "SCIENCE_TECHNOLOGY": "Science & Tech",
        "SOCIAL_ISSUES": "Social Issues",
        "INTERNAL_SECURITY": "Internal Security",
        "ETHICS": "Ethics",
        "INTERNATIONAL_RELATIONS": "International Relations",
    }
    return labels.get(cat_str, cat_str.replace("_", " ").title())


def format_current_affair_response(item: CurrentAffair) -> CurrentAffairResponse:
    pq_models: List[PotentialQuestionResponse] = []
    pq_dicts: List[Dict[str, Any]] = []

    for q in (item.questions or []):
        pq_models.append(
            PotentialQuestionResponse(
                id=q.id,
                question_text=q.question_text,
                question_type=q.question_type,
                difficulty=q.difficulty,
                explanation=q.explanation,
                why_this_matters=q.why_this_matters,
            )
        )
        pq_dicts.append({
            "id": q.id,
            "question": q.question_text,
            "type": q.question_type,
            "difficulty": q.difficulty,
            "explanation": q.explanation,
            "whyThisMatters": q.why_this_matters,
        })

    pub_date_str = item.published_at.strftime("%b %d, %Y") if item.published_at else ""

    return CurrentAffairResponse(
        id=item.id,
        title=item.title,
        slug=item.slug,
        summary=item.summary,
        source_name=item.source_name,
        source_url=item.source_url,
        published_at=item.published_at,
        retrieved_at=item.retrieved_at,
        category=item.category,
        categoryLabel=format_category_label(item.category),
        topic=item.topic,
        subtopic=item.subtopic,
        content=item.content,
        key_points=item.key_points or [],
        context=item.context,
        policy_response=item.policy_response,
        upsc_relevance=item.upsc_relevance,
        interview_angle=item.interview_angle,
        analysis_status=item.analysis_status,
        potential_questions=pq_models,
        created_at=item.created_at,
        updated_at=item.updated_at,
        # UI Aliases
        source=item.source_name,
        date=pub_date_str,
        whyItMatters=item.interview_angle or item.upsc_relevance,
        shortContext=item.context or item.summary,
        keyPoints=item.key_points or [],
        governmentResponse=item.policy_response,
        upscRelevance=item.upsc_relevance,
        interviewAngle=item.interview_angle,
        potentialQuestions=pq_dicts,
    )


@router.get("", response_model=CurrentAffairListResponse)
def list_current_affairs(
    category: Optional[str] = Query(None, description="Filter by category"),
    topic: Optional[str] = Query(None, description="Filter by topic"),
    source: Optional[str] = Query(None, description="Filter by source name"),
    search: Optional[str] = Query(None, description="Search keyword in title, summary, or content"),
    analysis_status: Optional[str] = Query(None, description="Filter by analysis status"),
    date_from: Optional[str] = Query(None, description="Published date range start"),
    date_to: Optional[str] = Query(None, description="Published date range end"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Items per page"),
    db: Session = Depends(get_db),
):
    """List current affairs with pagination and multi-field filtering."""
    query = db.query(CurrentAffair)

    if category:
        cat_upper = category.strip().upper().replace(" ", "_")
        query = query.filter(CurrentAffair.category == cat_upper)

    if topic:
        query = query.filter(CurrentAffair.topic.ilike(f"%{topic.strip()}%"))

    if source:
        query = query.filter(CurrentAffair.source_name.ilike(f"%{source.strip()}%"))

    if analysis_status:
        query = query.filter(CurrentAffair.analysis_status == analysis_status.strip().upper())

    if date_from:
        try:
            clean_df = date_from.strip().replace(" ", "+")
            df_dt = datetime.fromisoformat(clean_df)
            if df_dt.tzinfo is not None:
                df_dt = df_dt.astimezone(timezone.utc).replace(tzinfo=None)
            query = query.filter(CurrentAffair.published_at >= df_dt)
        except ValueError:
            pass

    if date_to:
        try:
            clean_dt = date_to.strip().replace(" ", "+")
            dt_dt = datetime.fromisoformat(clean_dt)
            if dt_dt.tzinfo is not None:
                dt_dt = dt_dt.astimezone(timezone.utc).replace(tzinfo=None)
            query = query.filter(CurrentAffair.published_at <= dt_dt)
        except ValueError:
            pass

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                CurrentAffair.title.ilike(term),
                CurrentAffair.summary.ilike(term),
                CurrentAffair.content.ilike(term),
                CurrentAffair.topic.ilike(term),
            )
        )

    total = query.count()
    pages = math.ceil(total / page_size) if total > 0 else 1
    offset = (page - 1) * page_size

    items = query.order_by(CurrentAffair.published_at.desc(), CurrentAffair.created_at.desc()).offset(offset).limit(page_size).all()

    formatted_items = [format_current_affair_response(item) for item in items]

    return CurrentAffairListResponse(
        items=formatted_items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/categories", response_model=CategoryListResponse)
def get_categories():
    """Return supported categories for current affairs."""
    cat_items = [
        CategoryItem(id=cat, name=cat, label=format_category_label(cat))
        for cat in VALID_CATEGORIES
    ]
    return CategoryListResponse(categories=cat_items)


@router.get("/topics", response_model=TopicListResponse)
def get_topics(db: Session = Depends(get_db)):
    """Return distinct active topics from current affairs."""
    topics = (
        db.query(CurrentAffair.topic)
        .filter(CurrentAffair.topic.isnot(None), CurrentAffair.topic != "")
        .distinct()
        .all()
    )
    topic_list = sorted([t[0] for t in topics if t[0]])
    return TopicListResponse(topics=topic_list)


@router.get("/{current_affair_id}", response_model=CurrentAffairResponse)
def get_current_affair(current_affair_id: str, db: Session = Depends(get_db)):
    """Retrieve detailed current affair record including practice questions."""
    item = db.query(CurrentAffair).filter(
        or_(CurrentAffair.id == current_affair_id, CurrentAffair.slug == current_affair_id)
    ).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Current Affair with ID or slug '{current_affair_id}' not found."
        )

    return format_current_affair_response(item)


@router.post("/{current_affair_id}/analyze", response_model=CurrentAffairResponse)
def analyze_current_affair(
    current_affair_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trigger grounded Gemini analysis & practice question generation for a current affair item."""
    item = db.query(CurrentAffair).filter(CurrentAffair.id == current_affair_id).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Current Affair with ID '{current_affair_id}' not found."
        )

    service = CurrentAffairsIngestionService(db=db)
    updated_item = service.analyze_and_publish(item)

    return format_current_affair_response(updated_item)
