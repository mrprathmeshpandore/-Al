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

    import time
    import numpy as np
    from app.services.cache_service import get_cache_service

    start_time = time.time()
    effective_top_k = top_k or settings.RAG_TOP_K
    filters = filters or {}

    # 1. Generate query embedding vector (with cache lookup)
    cache = get_cache_service()
    import hashlib
    query_hash = hashlib.sha256(clean_query.encode("utf-8")).hexdigest()
    cache_key = f"embed:query:{query_hash}"
    query_vector = cache.get(cache_key)

    if not query_vector:
        active_provider = provider or get_embedding_provider()
        query_vector = active_provider.embed_text(clean_query)
        if query_vector:
            cache.set(cache_key, query_vector, ttl=1800)

    if not query_vector:
        return {
            "query": clean_query,
            "results": [],
            "retrieval_latency_ms": round((time.time() - start_time) * 1000, 2),
            "message": "Failed to generate embedding vector for query."
        }

    # 2. Build Base Query joining specific columns rather than full ORM models
    q = db.query(
        DocumentChunk.id.label("chunk_id"),
        DocumentChunk.document_id.label("document_id"),
        DocumentChunk.page_number.label("page_number"),
        DocumentChunk.chunk_index.label("chunk_index"),
        DocumentChunk.content.label("content"),
        DocumentChunk.embedding.label("embedding"),
        DocumentChunk.chunk_metadata.label("chunk_metadata"),
        Resource.id.label("resource_id"),
        Resource.title.label("resource_title"),
        Resource.source.label("source"),
        Resource.subject.label("subject"),
        Resource.topic.label("topic"),
        Resource.category.label("category"),
    )\
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
    else:
        q = q.filter(Resource.is_official == True)

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
            "retrieval_latency_ms": round((time.time() - start_time) * 1000, 2),
            "message": "No sufficiently relevant content found."
        }

    # 5. Fast Vector Cosine Similarity (Vectorized NumPy Matrix Dot Product)
    q_vec = np.array(query_vector, dtype=np.float32)
    q_norm = np.linalg.norm(q_vec)
    min_threshold = settings.RAG_MIN_SIMILARITY

    scored_results = []
    
    if q_norm > 0:
        embeddings_list = []
        valid_items = []
        for item in items:
            vec = item.embedding
            if vec and len(vec) == len(query_vector):
                embeddings_list.append(vec)
                valid_items.append(item)

        if embeddings_list:
            emb_matrix = np.array(embeddings_list, dtype=np.float32)
            emb_norms = np.linalg.norm(emb_matrix, axis=1)
            # Prevent division by zero
            emb_norms[emb_norms == 0] = 1.0

            # Matrix dot product across all chunks simultaneously
            scores = (emb_matrix @ q_vec) / (emb_norms * q_norm)

            for idx, score in enumerate(scores):
                float_score = float(score)
                if float_score >= min_threshold:
                    item = valid_items[idx]
                    scored_results.append({
                        "chunk_id": item.chunk_id,
                        "document_id": item.document_id,
                        "resource_id": item.resource_id,
                        "resource_title": item.resource_title,
                        "content": item.content,
                        "page_number": item.page_number,
                        "chunk_index": item.chunk_index,
                        "score": round(float_score, 4),
                        "source": item.source,
                        "subject": item.subject,
                        "topic": item.topic,
                        "category": item.category,
                        "metadata": item.chunk_metadata or {},
                    })

    # Sort results by score descending
    scored_results.sort(key=lambda x: x["score"], reverse=True)
    top_results = scored_results[:effective_top_k]

    retrieval_latency_ms = round((time.time() - start_time) * 1000, 2)

    if not top_results:
        return {
            "query": clean_query,
            "results": [],
            "retrieval_latency_ms": retrieval_latency_ms,
            "message": "No sufficiently relevant content found."
        }

    return {
        "query": clean_query,
        "results": top_results,
        "retrieval_latency_ms": retrieval_latency_ms,
        "message": f"Successfully retrieved top {len(top_results)} relevant knowledge chunks."
    }
