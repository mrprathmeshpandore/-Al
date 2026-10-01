import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.retrieval_service import search_knowledge_base
from app.services.context_builder import build_rag_context
from app.services.citation_service import build_backend_citations
from app.services.gemini_service import get_gemini_service, BaseGeminiService

logger = logging.getLogger("rag_answer_service")

GROUNDED_SYSTEM_INSTRUCTION = (
    "You are an expert AI assistant for Prashasak AI — an AI-Powered UPSC Interview Preparation Platform.\n"
    "Your task is to provide accurate, grounded answers to the user's question using ONLY the provided retrieved sources.\n\n"
    "STRICT GROUNDEDNESS RULES:\n"
    "1. Answer strictly using ONLY the retrieved source context provided in the prompt.\n"
    "2. Do NOT invent, extrapolate, or fabricate any facts, statistics, page numbers, titles, quotations, constitutional provisions, or government schemes.\n"
    "3. Do NOT supplement with unsupported general knowledge.\n"
    "4. If the retrieved context is insufficient or irrelevant to answer the question completely, set \"grounded\": false and state clearly: "
    "\"I could not find sufficiently relevant information in the available Prashasak AI resources.\"\n"
    "5. Clearly distinguish source-supported facts from explanation. Keep responses concise, objective, and relevant for UPSC aspirants.\n"
    "6. Never treat generated text as an official UPSC statement.\n"
    "7. Output strictly as JSON with keys: \"answer\" (string), \"grounded\" (boolean), and \"source_indexes\" (list of integers matching 1-indexed source numbers used)."
)

SAFE_UNGROUNDED_ANSWER = "I could not find sufficiently relevant information in the available Prashasak AI resources."


def generate_rag_grounded_answer(
    query: str,
    current_user_id: str,
    db: Session,
    top_k: Optional[int] = None,
    filters: Optional[Dict[str, Any]] = None,
    gemini_service: Optional[BaseGeminiService] = None,
    embedding_provider: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Core RAG Grounded Answer Pipeline:
    1. User Query -> Retrieval Service (Vector Search)
    2. Check similarity threshold & retrieval completeness
    3. If insufficient context -> Return safe ungrounded response immediately (No Gemini call)
    4. If context valid -> Build structured context string
    5. Invoke Gemini Service for grounded generation
    6. Construct backend citations strictly from retrieved DB chunks
    7. Return final response object
    """
    k = top_k or settings.RAG_TOP_K
    filters_dict = filters or {}

    # Step 1: Vector Search via Retrieval Engine
    retrieval_res = search_knowledge_base(
        query=query,
        top_k=k,
        filters=filters_dict,
        current_user_id=current_user_id,
        db=db,
        provider=embedding_provider,
    )

    retrieved_chunks = retrieval_res.get("results", [])

    # Step 2: Validate similarity threshold and chunk existence
    has_valid_chunks = False
    if retrieved_chunks:
        top_score = float(retrieved_chunks[0].get("score", 0.0))
        if top_score >= settings.RAG_MIN_SIMILARITY:
            has_valid_chunks = True

    # Step 3: If no valid chunks match threshold, return safe response immediately WITHOUT invoking Gemini
    if not has_valid_chunks:
        logger.info(f"No chunks retrieved above similarity threshold {settings.RAG_MIN_SIMILARITY} for query '{query}'. Returning safe fallback.")
        return {
            "query": query,
            "answer": SAFE_UNGROUNDED_ANSWER,
            "grounded": False,
            "sources": [],
        }

    # Step 4: Build context from retrieved chunks
    context_text = build_rag_context(retrieved_chunks)
    prompt = f"RETRIEVED CONTEXT:\n{context_text}\n\nUSER QUESTION:\n{query}"

    # Step 5: Send context + query to Gemini Service
    active_gemini_service = gemini_service or get_gemini_service()

    try:
        gemini_result = active_gemini_service.generate_grounded_answer(
            prompt=prompt,
            system_instruction=GROUNDED_SYSTEM_INSTRUCTION,
        )
    except Exception as e:
        logger.error(f"Gemini generation service exception: {e}")
        return {
            "query": query,
            "answer": SAFE_UNGROUNDED_ANSWER,
            "grounded": False,
            "sources": [],
        }

    answer_text = gemini_result.get("answer", SAFE_UNGROUNDED_ANSWER)
    is_grounded = bool(gemini_result.get("grounded", False))
    source_indexes = gemini_result.get("source_indexes", [])

    # Step 6: Construct backend citations strictly from retrieved chunks
    if is_grounded and answer_text != SAFE_UNGROUNDED_ANSWER:
        citations = build_backend_citations(retrieved_chunks, referenced_source_indexes=source_indexes)
    else:
        citations = []
        is_grounded = False

    return {
        "query": query,
        "answer": answer_text,
        "grounded": is_grounded,
        "sources": citations,
    }
