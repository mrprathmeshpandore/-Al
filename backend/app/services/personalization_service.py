import re
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.models.profile import UserProfile
from app.models.question import InterviewQuestion, InterviewQuestionSource
from app.services.daf_context_builder import extract_daf_topic_and_context
from app.services.retrieval_service import search_knowledge_base
from app.services.context_builder import build_rag_context
from app.services.citation_service import build_backend_citations
from app.services.gemini_service import get_gemini_service, BaseGeminiService
from app.services.question_validation_service import validate_generated_question
from app.services.question_generation_service import check_is_duplicate, UNGROUNDED_QUESTION_MESSAGE

logger = logging.getLogger("personalization_service")

PERSONALIZED_QUESTION_SYSTEM_INSTRUCTION = (
    "You are an expert UPSC Civil Services Personality Test question-generation assistant for Prashasak AI.\n"
    "Your objective is to generate ONE high-quality, personalized interview practice question connecting the candidate's actual DAF profile background with the provided retrieved knowledge context.\n\n"
    "STRICT PERSONALIZATION & TERMINOLOGY RULES:\n"
    "1. Base candidate background STRICTLY on the explicit DAF PROFILE text provided. Do NOT assume unstated candidate achievements, experiences, religion, caste, ethnicity, or political affiliation.\n"
    "2. Ground knowledge context strictly in the retrieved source block.\n"
    "3. NEVER claim or imply that this question will be asked in an actual UPSC interview.\n"
    "4. NEVER use misleading phrases like 'UPSC will definitely ask this' or '100% guaranteed question'.\n"
    "5. Frame an insightful question suitable for UPSC personality test (testing reasoning, ethics, administrative perspective, or constitutional values).\n"
    "6. Output strictly as a JSON object with keys:\n"
    "   - \"question\": string (the personalized interview practice question text)\n"
    "   - \"why_this_matters\": string (significance of connecting this DAF background to governance/public policy)\n"
    "   - \"explanation\": string (analytical perspective/background)\n"
    "   - \"grounded\": boolean (true if context was sufficient)\n"
    "   - \"source_indexes\": list of integers (1-indexed matching the source numbers used from context)"
)


def generate_personalized_interview_question(
    source: Optional[str] = None,
    personalization_source: Optional[str] = None,
    current_user: Optional[User] = None,
    current_user_id: Optional[str] = None,
    db: Session = None,
    difficulty: Optional[str] = "MODERATE",
    question_type: Optional[str] = "MAIN",
    top_k: Optional[int] = 5,
    gemini_service: Optional[BaseGeminiService] = None,
    embedding_provider: Optional[Any] = None,
    retrieval_func: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    RAG + DAF Personalized Question Generation Pipeline:
    1. Fetch authenticated user's UserProfile
    2. Extract DAF context & focused topic query via `daf_context_builder.py`
    3. Safe fallback if DAF field unavailable (No Gemini call)
    4. RAG Knowledge Retrieval via `retrieval_service.py`
    5. Similarity threshold check (`RAG_MIN_SIMILARITY`)
    6. Safe fallback if knowledge chunks insufficient (No Gemini call)
    7. Gemini Generation with DAF + RAG prompt context
    8. Question Quality & Terminology Validation
    9. Duplicate Question Detection
    10. Backend Citation Construction
    11. Database Persistence (`interview_questions` & `interview_question_sources`)
    12. Return structured result
    """
    effective_source = source or personalization_source or "EDUCATION"
    src_clean = effective_source.upper().strip()

    effective_user_id = None
    if current_user and hasattr(current_user, "id"):
        effective_user_id = current_user.id
    elif current_user_id:
        effective_user_id = current_user_id

    # Step 1: Read Candidate Profile from Database
    profile = db.query(UserProfile).filter(UserProfile.user_id == effective_user_id).first() if effective_user_id else None

    # Step 2: Extract DAF Context & Topic Query
    daf_info = extract_daf_topic_and_context(profile=profile, source_type=src_clean)

    # Step 3: If DAF field unavailable, return safe ungrounded response immediately WITHOUT calling Gemini
    if not daf_info:
        logger.info(f"Requested DAF source '{src_clean}' is empty or unavailable for user {effective_user_id}.")
        return {
            "id": None,
            "question": UNGROUNDED_QUESTION_MESSAGE,
            "question_text": UNGROUNDED_QUESTION_MESSAGE,
            "question_type": question_type or "MAIN",
            "difficulty": difficulty or "MODERATE",
            "subject": None,
            "topic": None,
            "category": None,
            "is_personalized": False,
            "personalized": False,
            "personalization_source": src_clean,
            "personalization_label": None,
            "why_this_matters": None,
            "explanation": None,
            "grounded": False,
            "sources": [],
            "citation_sources": [],
            "message": "The selected DAF information is not available in your profile.",
        }

    daf_context_str = daf_info["daf_context"]
    topic_query = daf_info["topic_query"]
    label = daf_info["label"]
    subject_hint = daf_info["subject_hint"]

    # Step 4: Vector RAG Search
    k = top_k or settings.RAG_TOP_K
    if retrieval_func:
        retrieved_chunks = retrieval_func(query=topic_query, top_k=k, user_id=effective_user_id, db=db)
    else:
        retrieval_res = search_knowledge_base(
            query=topic_query,
            top_k=k,
            filters={},
            current_user_id=effective_user_id,
            db=db,
            provider=embedding_provider,
        )
        retrieved_chunks = retrieval_res.get("results", [])

    # Step 5: Validate similarity threshold
    has_valid_chunks = False
    if retrieved_chunks:
        top_score = float(retrieved_chunks[0].get("score", retrieved_chunks[0].get("similarity_score", 0.0)))
        if top_score >= settings.RAG_MIN_SIMILARITY:
            has_valid_chunks = True

    # Step 6: If no valid RAG chunks match threshold, return safe response WITHOUT calling Gemini
    if not has_valid_chunks:
        logger.info(f"No RAG chunks met threshold {settings.RAG_MIN_SIMILARITY} for personalized query '{topic_query}'.")
        return {
            "id": None,
            "question": UNGROUNDED_QUESTION_MESSAGE,
            "question_text": UNGROUNDED_QUESTION_MESSAGE,
            "question_type": question_type or "MAIN",
            "difficulty": difficulty or "MODERATE",
            "subject": subject_hint,
            "topic": label,
            "category": None,
            "is_personalized": False,
            "personalized": False,
            "personalization_source": src_clean,
            "personalization_label": label,
            "why_this_matters": None,
            "explanation": None,
            "grounded": False,
            "sources": [],
            "citation_sources": [],
            "message": UNGROUNDED_QUESTION_MESSAGE,
        }

    # Step 7: Build Combined DAF + RAG Prompt Context
    rag_context_str = build_rag_context(retrieved_chunks)
    prompt = (
        f"{daf_context_str}\n\n"
        f"RETRIEVED KNOWLEDGE CONTEXT:\n{rag_context_str}\n\n"
        f"REQUESTED PARAMETERS:\n"
        f"- Personalization Source: {src_clean}\n"
        f"- DAF Background Label: {label}\n"
        f"- Question Type: {question_type or 'MAIN'}\n"
        f"- Difficulty Level: {difficulty or 'MODERATE'}\n\n"
        f"Generate a potential personalized UPSC interview practice question respecting all rules."
    )

    # Step 8: Invoke Gemini Generation Service
    active_gemini_service = gemini_service or get_gemini_service()

    try:
        gemini_res = active_gemini_service.generate_grounded_answer(
            prompt=prompt,
            system_instruction=PERSONALIZED_QUESTION_SYSTEM_INSTRUCTION,
        )
    except Exception as e:
        logger.error(f"Gemini generation exception during personalized question creation: {e}")
        return {
            "id": None,
            "question": UNGROUNDED_QUESTION_MESSAGE,
            "question_text": UNGROUNDED_QUESTION_MESSAGE,
            "question_type": question_type or "MAIN",
            "difficulty": difficulty or "MODERATE",
            "subject": subject_hint,
            "topic": label,
            "category": None,
            "is_personalized": False,
            "personalized": False,
            "personalization_source": src_clean,
            "personalization_label": label,
            "why_this_matters": None,
            "explanation": None,
            "grounded": False,
            "sources": [],
            "citation_sources": [],
            "message": "Personalized question generation failed due to AI service exception.",
        }

    # Step 9: Validate Question Output & Rules
    is_valid, reason = validate_generated_question(gemini_res)
    if not is_valid:
        logger.warning(f"Personalized question failed validation: {reason}")
        return {
            "id": None,
            "question": UNGROUNDED_QUESTION_MESSAGE,
            "question_text": UNGROUNDED_QUESTION_MESSAGE,
            "question_type": question_type or "MAIN",
            "difficulty": difficulty or "MODERATE",
            "subject": subject_hint,
            "topic": label,
            "category": None,
            "is_personalized": False,
            "personalized": False,
            "personalization_source": src_clean,
            "personalization_label": label,
            "why_this_matters": None,
            "explanation": None,
            "grounded": False,
            "sources": [],
            "citation_sources": [],
            "message": f"Question validation failed: {reason}",
        }

    q_text = str(gemini_res.get("answer") or gemini_res.get("question") or gemini_res.get("question_text", "")).strip()
    why_matters = str(gemini_res.get("why_this_matters", "")).strip()
    explanation = str(gemini_res.get("explanation", "")).strip()
    is_grounded = bool(gemini_res.get("grounded", True))
    source_indexes = gemini_res.get("source_indexes", [])

    # Step 10: Duplicate Check
    is_dup = check_is_duplicate(user_id=effective_user_id, question_text=q_text, db=db)
    if is_dup:
        logger.info(f"Duplicate personalized question detected for user {effective_user_id}: '{q_text}'. Regenerating or returning existing.")
        existing_q = (
            db.query(InterviewQuestion)
            .filter(InterviewQuestion.user_id == effective_user_id, InterviewQuestion.question_text == q_text)
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
                "question_text": existing_q.question_text,
                "question_type": existing_q.question_type,
                "difficulty": existing_q.difficulty,
                "subject": existing_q.subject,
                "topic": existing_q.topic,
                "category": existing_q.category,
                "is_personalized": existing_q.is_personalized,
                "personalized": existing_q.is_personalized,
                "personalization_source": existing_q.personalization_source,
                "personalization_label": existing_q.personalization_label,
                "why_this_matters": existing_q.why_this_matters,
                "explanation": existing_q.explanation,
                "grounded": True,
                "sources": sources_list,
                "citation_sources": sources_list,
                "created_at": existing_q.created_at,
            }

    # Step 11: Construct Backend Citations
    citations = build_backend_citations(retrieved_chunks, referenced_source_indexes=source_indexes)

    # Step 12: Database Persistence
    db_question = InterviewQuestion(
        user_id=effective_user_id,
        question_text=q_text,
        question_type=question_type or "MAIN",
        difficulty=difficulty or "MODERATE",
        subject=subject_hint,
        topic=label,
        category=src_clean,
        is_personalized=True,
        personalization_source=src_clean,
        personalization_label=label,
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
        "question_text": db_question.question_text,
        "question_type": db_question.question_type,
        "difficulty": db_question.difficulty,
        "subject": db_question.subject,
        "topic": db_question.topic,
        "category": db_question.category,
        "is_personalized": True,
        "personalized": True,
        "personalization_source": src_clean,
        "personalization_label": label,
        "why_this_matters": db_question.why_this_matters,
        "explanation": db_question.explanation,
        "grounded": is_grounded,
        "sources": citations,
        "citation_sources": citations,
        "created_at": db_question.created_at,
    }
