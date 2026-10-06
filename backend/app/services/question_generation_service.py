import re
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.config import settings
from app.models.question import InterviewQuestion, InterviewQuestionSource
from app.services.retrieval_service import search_knowledge_base
from app.services.context_builder import build_rag_context
from app.services.citation_service import build_backend_citations
from app.services.gemini_service import get_gemini_service, BaseGeminiService
from app.services.question_validation_service import validate_generated_question

logger = logging.getLogger("question_generation_service")

QUESTION_SYSTEM_INSTRUCTION = (
    "You are an expert UPSC Civil Services Personality Test question-generation assistant for Prashasak AI.\n"
    "Your primary objective is to generate ONE high-quality, potential UPSC interview practice question grounded strictly in the provided retrieved context.\n\n"
    "STRICT GROUNDEDNESS & TERMINOLOGY RULES:\n"
    "1. Base the interview practice question strictly on the provided retrieved source context.\n"
    "2. Do NOT fabricate facts, statistics, constitutional provisions, government schemes, or court judgments.\n"
    "3. NEVER claim or imply that this question will be asked in an actual UPSC interview.\n"
    "4. NEVER use misleading phrases like 'UPSC will definitely ask this' or '100% guaranteed question'.\n"
    "5. Frame questions that test analytical thinking, constitutional morality, governance perspective, ethical reasoning, or administrative decision-making.\n"
    "6. Avoid trivial memory/textbook questions. Encourage balanced, objective, and well-reasoned answers suitable for a civil services candidate.\n"
    "7. Output strictly as a JSON object with keys:\n"
    "   - \"question\": string (the practice question text)\n"
    "   - \"why_this_matters\": string (why this topic/perspective is relevant for UPSC personality test)\n"
    "   - \"explanation\": string (analytical context/background)\n"
    "   - \"grounded\": boolean (true if context was sufficient)\n"
    "   - \"source_indexes\": list of integers (1-indexed matching the source numbers used from context)"
)

UNGROUNDED_QUESTION_MESSAGE = "Insufficient relevant knowledge was found to generate a grounded question from the available resources."


def normalize_text(text: str) -> str:
    """Normalizes string for robust duplicate detection (lowercase, remove punctuation, collapse whitespace)."""
    clean = re.sub(r"[^\w\s]", "", text.lower())
    return " ".join(clean.split())


def check_is_duplicate(user_id: str, question_text: str, db: Session) -> bool:
    """Checks if a user already has an identical or near-identical saved question."""
    norm_input = normalize_text(question_text)
    if not norm_input:
        return False

    existing_questions = (
        db.query(InterviewQuestion)
        .filter(InterviewQuestion.user_id == user_id, InterviewQuestion.status == "ACTIVE")
        .all()
    )

    for eq in existing_questions:
        if normalize_text(eq.question_text) == norm_input:
            return True
    return False


def generate_interview_question(
    topic: str,
    current_user_id: str,
    db: Session,
    subject: Optional[str] = None,
    category: Optional[str] = None,
    difficulty: Optional[str] = "MODERATE",
    question_type: Optional[str] = "MAIN",
    top_k: Optional[int] = 5,
    language: Optional[str] = "en-IN",
    gemini_service: Optional[BaseGeminiService] = None,
    embedding_provider: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    RAG-Grounded UPSC Interview Question Generation Pipeline:
    1. Input validation
    2. Vector Search via Retrieval Engine (`retrieval_service.py`)
    3. Similarity threshold validation (`RAG_MIN_SIMILARITY`)
    4. Safe fallback if insufficient chunks (No Gemini call)
    5. Context Builder formatting
    6. Gemini Question Generation
    7. Question Validation & Prohibited Terminology check
    8. Duplicate Question Detection
    9. Backend Citation Construction
    10. Database Persistence (`interview_questions` & `interview_question_sources`)
    11. Return response object
    """
    k = top_k or settings.RAG_TOP_K
    filters = {}
    if subject:
        filters["subject"] = subject
    if category:
        filters["category"] = category

    # Step 1: Search Knowledge Base
    retrieval_res = search_knowledge_base(
        query=topic,
        top_k=k,
        filters=filters,
        current_user_id=current_user_id,
        db=db,
        provider=embedding_provider,
    )

    retrieved_chunks = retrieval_res.get("results", [])

    # Step 2: Validate similarity threshold
    has_valid_chunks = False
    if retrieved_chunks:
        top_score = float(retrieved_chunks[0].get("score", 0.0))
        if top_score >= settings.RAG_MIN_SIMILARITY:
            has_valid_chunks = True

    # Step 3: If no valid chunks, return safe ungrounded response immediately WITHOUT calling Gemini
    if not has_valid_chunks:
        logger.info(f"No chunks found matching similarity threshold {settings.RAG_MIN_SIMILARITY} for topic '{topic}'.")
        return {
            "id": None,
            "question": UNGROUNDED_QUESTION_MESSAGE,
            "question_type": question_type or "MAIN",
            "difficulty": difficulty or "MODERATE",
            "subject": subject,
            "topic": topic,
            "category": category,
            "why_this_matters": None,
            "explanation": None,
            "grounded": False,
            "sources": [],
            "message": UNGROUNDED_QUESTION_MESSAGE,
        }

    # Step 4: Build Context String & Language Target
    target_lang_name = "English"
    if language:
        clean_l = language.lower()
        if "mr" in clean_l or "marathi" in clean_l:
            target_lang_name = "Marathi (मराठी)"
        elif "hi" in clean_l or "hindi" in clean_l:
            target_lang_name = "Hindi (हिंदी)"

    context_text = build_rag_context(retrieved_chunks)
    prompt = (
        f"RETRIEVED KNOWLEDGE CONTEXT:\n{context_text}\n\n"
        f"REQUESTED PARAMETERS:\n"
        f"- Topic: {topic}\n"
        f"- Subject: {subject or 'General'}\n"
        f"- Question Type: {question_type or 'MAIN'}\n"
        f"- Difficulty Level: {difficulty or 'MODERATE'}\n"
        f"- Target Language: {target_lang_name}\n\n"
        f"CRITICAL LANGUAGE RULE: Generate the question, explanation, and why_this_matters strictly in {target_lang_name}. If Marathi or Hindi, write clean Devanagari script suitable for a civil services interview.\n\n"
        f"Generate a potential UPSC interview practice question respecting all rules."
    )

    # Step 5: Invoke Gemini Service
    active_gemini_service = gemini_service or get_gemini_service()

    try:
        gemini_res = active_gemini_service.generate_grounded_answer(
            prompt=prompt,
            system_instruction=QUESTION_SYSTEM_INSTRUCTION,
        )
    except Exception as e:
        logger.error(f"Gemini service exception during question generation: {e}")
        return {
            "id": None,
            "question": UNGROUNDED_QUESTION_MESSAGE,
            "question_type": question_type or "MAIN",
            "difficulty": difficulty or "MODERATE",
            "subject": subject,
            "topic": topic,
            "category": category,
            "why_this_matters": None,
            "explanation": None,
            "grounded": False,
            "sources": [],
            "message": "Question generation failed due to AI service exception.",
        }

    # Step 6: Validate Question Output & Rules
    is_valid, reason = validate_generated_question(gemini_res)
    if not is_valid:
        logger.warning(f"Generated question failed validation: {reason}")
        return {
            "id": None,
            "question": UNGROUNDED_QUESTION_MESSAGE,
            "question_type": question_type or "MAIN",
            "difficulty": difficulty or "MODERATE",
            "subject": subject,
            "topic": topic,
            "category": category,
            "why_this_matters": None,
            "explanation": None,
            "grounded": False,
            "sources": [],
            "message": f"Question validation failed: {reason}",
        }

    q_text = str(gemini_res.get("answer") or gemini_res.get("question", "")).strip()
    why_matters = str(gemini_res.get("why_this_matters", "")).strip()
    explanation = str(gemini_res.get("explanation", "")).strip()
    is_grounded = bool(gemini_res.get("grounded", True))
    source_indexes = gemini_res.get("source_indexes", [])

    # Step 7: Duplicate Check
    is_dup = check_is_duplicate(user_id=current_user_id, question_text=q_text, db=db)
    if is_dup:
        logger.info(f"Duplicate question detected for user {current_user_id}: '{q_text}'. Returning existing matching question.")
        existing_q = (
            db.query(InterviewQuestion)
            .filter(InterviewQuestion.user_id == current_user_id, InterviewQuestion.question_text == q_text)
            .first()
        )
        if existing_q:
            sources_list = [
                {
                    "resource_id": s.resource_id,
                    "document_id": s.document_id,
                    "chunk_id": s.chunk_id,
                    "resource_title": s.resource_title,
                    "page_number": s.page_number,
                    "chunk_index": s.chunk_index,
                    "score": s.similarity_score,
                }
                for s in existing_q.sources
            ]
            return {
                "id": existing_q.id,
                "question": existing_q.question_text,
                "question_type": existing_q.question_type,
                "difficulty": existing_q.difficulty,
                "subject": existing_q.subject,
                "topic": existing_q.topic,
                "category": existing_q.category,
                "why_this_matters": existing_q.why_this_matters,
                "explanation": existing_q.explanation,
                "grounded": True,
                "sources": sources_list,
                "created_at": existing_q.created_at,
            }

    # Step 8: Construct Backend Citations
    citations = build_backend_citations(retrieved_chunks, referenced_source_indexes=source_indexes)

    # Step 9: Database Persistence
    db_question = InterviewQuestion(
        user_id=current_user_id,
        question_text=q_text,
        question_type=question_type or "MAIN",
        difficulty=difficulty or "MODERATE",
        subject=subject,
        topic=topic,
        category=category,
        explanation=explanation,
        why_this_matters=why_matters,
        status="ACTIVE",
    )
    db.add(db_question)
    db.flush()

    for c in citations:
        db_source = InterviewQuestionSource(
            question_id=db_question.id,
            resource_id=c.get("resource_id"),
            document_id=c.get("document_id"),
            chunk_id=c.get("chunk_id"),
            resource_title=c.get("resource_title", "Untitled Resource"),
            page_number=c.get("page_number"),
            chunk_index=c.get("chunk_index"),
            similarity_score=c.get("score"),
        )
        db.add(db_source)

    db.commit()
    db.refresh(db_question)

    return {
        "id": db_question.id,
        "question": db_question.question_text,
        "question_type": db_question.question_type,
        "difficulty": db_question.difficulty,
        "subject": db_question.subject,
        "topic": db_question.topic,
        "category": db_question.category,
        "why_this_matters": db_question.why_this_matters,
        "explanation": db_question.explanation,
        "grounded": is_grounded,
        "sources": citations,
        "created_at": db_question.created_at,
    }


def list_user_questions(
    user_id: str,
    db: Session,
    page: int = 1,
    page_size: int = 10,
    subject: Optional[str] = None,
    topic: Optional[str] = None,
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    question_type: Optional[str] = None,
    is_personalized: Optional[bool] = None,
    personalization_source: Optional[str] = None,
) -> Dict[str, Any]:
    """Retrieves paginated list of user's saved practice questions with optional metadata filters."""
    query = db.query(InterviewQuestion).filter(
        InterviewQuestion.user_id == user_id,
        InterviewQuestion.status == "ACTIVE"
    )

    if subject:
        query = query.filter(InterviewQuestion.subject == subject)
    if topic:
        query = query.filter(InterviewQuestion.topic.ilike(f"%{topic}%"))
    if category:
        query = query.filter(InterviewQuestion.category == category)
    if difficulty:
        query = query.filter(InterviewQuestion.difficulty == difficulty.upper())
    if question_type:
        query = query.filter(InterviewQuestion.question_type == question_type.upper())
    if is_personalized is not None:
        query = query.filter(InterviewQuestion.is_personalized == is_personalized)
    if personalization_source:
        query = query.filter(InterviewQuestion.personalization_source == personalization_source.upper())

    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(InterviewQuestion.created_at.desc()).offset(offset).limit(page_size).all()

    result_list = []
    for item in items:
        sources_list = [
            {
                "resource_id": s.resource_id,
                "document_id": s.document_id,
                "chunk_id": s.chunk_id,
                "resource_title": s.resource_title,
                "page_number": s.page_number,
                "chunk_index": s.chunk_index,
                "score": s.similarity_score,
            }
            for s in item.sources
        ]
        result_list.append({
            "id": item.id,
            "question": item.question_text,
            "question_type": item.question_type,
            "difficulty": item.difficulty,
            "subject": item.subject,
            "topic": item.topic,
            "category": item.category,
            "is_personalized": item.is_personalized,
            "personalization_source": item.personalization_source,
            "personalization_label": item.personalization_label,
            "why_this_matters": item.why_this_matters,
            "explanation": item.explanation,
            "grounded": True,
            "sources": sources_list,
            "created_at": item.created_at,
        })

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "questions": result_list,
    }


def get_user_question_by_id(question_id: str, user_id: str, db: Session) -> Optional[Dict[str, Any]]:
    """Fetches single practice question by ID enforcing user isolation."""
    item = (
        db.query(InterviewQuestion)
        .filter(
            InterviewQuestion.id == question_id,
            InterviewQuestion.user_id == user_id,
            InterviewQuestion.status == "ACTIVE"
        )
        .first()
    )
    if not item:
        return None

    sources_list = [
        {
            "resource_id": s.resource_id,
            "document_id": s.document_id,
            "chunk_id": s.chunk_id,
            "resource_title": s.resource_title,
            "page_number": s.page_number,
            "chunk_index": s.chunk_index,
            "score": s.similarity_score,
        }
        for s in item.sources
    ]

    return {
        "id": item.id,
        "question": item.question_text,
        "question_type": item.question_type,
        "difficulty": item.difficulty,
        "subject": item.subject,
        "topic": item.topic,
        "category": item.category,
        "is_personalized": item.is_personalized,
        "personalization_source": item.personalization_source,
        "personalization_label": item.personalization_label,
        "why_this_matters": item.why_this_matters,
        "explanation": item.explanation,
        "grounded": True,
        "sources": sources_list,
        "created_at": item.created_at,
    }


def delete_user_question_by_id(question_id: str, user_id: str, db: Session) -> bool:
    """Soft deletes/archives a practice question enforcing user isolation."""
    item = (
        db.query(InterviewQuestion)
        .filter(InterviewQuestion.id == question_id, InterviewQuestion.user_id == user_id)
        .first()
    )
    if not item:
        return False

    db.delete(item)
    db.commit()
    return True
