import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.config import settings
from app.models.resource import Resource
from app.models.document import Document
from app.models.document_chunk import DocumentChunk, EmbeddingStatus
from app.services.embedding_provider import get_embedding_provider

logger = logging.getLogger("retrieval_service")


def compute_cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Computes cosine similarity score between two float vectors."""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm_a = sum(a * a for a in vec1) ** 0.5
    norm_b = sum(b * b for b in vec2) ** 0.5

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return float(dot_product / (norm_a * norm_b))


def search_knowledge_base(
    query: str,
    top_k: Optional[int] = None,
    filters: Optional[Dict[str, Any]] = None,
    current_user_id: Optional[str] = None,
    db: Session = None,
    provider = None
) -> Dict[str, Any]:
    """
    RAG Knowledge Retrieval Engine:
    Validates query -> Generates query vector -> Applies authorization & metadata filters -> Performs vector cosine search -> Enforces similarity threshold -> Packages citation metadata.
    """
    clean_query = (query or "").strip()
    if not clean_query:
        return {
            "query": "",
            "results": [],
            "message": "Query string must not be empty."
        }

    effective_top_k = top_k or settings.RAG_TOP_K
    filters = filters or {}

    # 1. Generate query embedding vector
    active_provider = provider or get_embedding_provider()
    query_vector = active_provider.embed_text(clean_query)

    if not query_vector:
        return {
            "query": clean_query,
            "results": [],
            "message": "Failed to generate embedding vector for query."
        }

    # 2. Build Base Query joining DocumentChunk -> Document -> Resource
    q = db.query(DocumentChunk, Document, Resource)\
        .join(Document, DocumentChunk.document_id == Document.id)\
        .join(Resource, Document.resource_id == Resource.id)\
        .filter(DocumentChunk.embedding_status == EmbeddingStatus.COMPLETED.value)\
        .filter(DocumentChunk.embedding.isnot(None))

    # 3. User Authorization: allow official/public resources OR user's own resources
    if current_user_id:
        q = q.filter(
            or_(
                Resource.is_official == True,
                Resource.created_by == current_user_id
            )
        )

    # 4. Apply Metadata Filters
    if filters.get("subject"):
        q = q.filter(Resource.subject.ilike(f"%{filters['subject']}%"))
    if filters.get("category"):
        q = q.filter(Resource.category.ilike(f"%{filters['category']}%"))
    if filters.get("topic"):
        q = q.filter(Resource.topic.ilike(f"%{filters['topic']}%"))
    if filters.get("resource_id"):
        q = q.filter(Resource.id == filters["resource_id"])
    if filters.get("document_id"):
        q = q.filter(DocumentChunk.document_id == filters["document_id"])

    items = q.all()

    if not items:
        return {
            "query": clean_query,
            "results": [],
            "message": "No sufficiently relevant content found."
        }

    # 5. Compute Vector Cosine Similarity
    scored_results = []
    min_threshold = settings.RAG_MIN_SIMILARITY

    for chunk, doc, resource in items:
        chunk_vec = chunk.embedding or []
        score = compute_cosine_similarity(query_vector, chunk_vec)

        if score >= min_threshold:
            scored_results.append({
                "chunk_id": chunk.id,
                "document_id": doc.id,
                "resource_id": resource.id,
                "resource_title": resource.title,
                "content": chunk.content,
                "page_number": chunk.page_number,
                "chunk_index": chunk.chunk_index,
                "score": round(score, 4),
                "source": resource.source,
                "subject": resource.subject,
                "topic": resource.topic,
                "category": resource.category,
                "metadata": chunk.chunk_metadata or {},
            })

    # Sort results by score descending
    scored_results.sort(key=lambda x: x["score"], reverse=True)
    top_results = scored_results[:effective_top_k]

    if not top_results:
        return {
            "query": clean_query,
            "results": [],
            "message": "No sufficiently relevant content found."
        }

    return {
        "query": clean_query,
        "results": top_results,
        "message": f"Successfully retrieved top {len(top_results)} relevant knowledge chunks."
    }
