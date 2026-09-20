import hashlib
import logging
from typing import List, Dict, Any, Optional

from app.services.embedding_provider import BaseEmbeddingProvider, get_embedding_provider
from app.models.document_chunk import EmbeddingStatus

logger = logging.getLogger("embedding_service")


def compute_content_hash(text: str) -> str:
    """Computes SHA-256 hash of chunk content for idempotency tracking."""
    return hashlib.sha256(text.strip().encode('utf-8')).hexdigest()


def process_chunk_embeddings(
    chunks: List[Dict[str, Any]],
    provider: Optional[BaseEmbeddingProvider] = None
) -> List[Dict[str, Any]]:
    """
    Service responsible for batch embedding generation and content hashing for document chunks.
    """
    if not chunks:
        return []

    active_provider = provider or get_embedding_provider()
    texts = [c.get("content", "") for c in chunks]

    # Compute content hashes
    hashes = [compute_content_hash(t) for t in texts]

    try:
        # Generate vectors via active embedding provider
        vectors = active_provider.embed_documents(texts)

        processed_chunks = []
        for i, chunk_data in enumerate(chunks):
            vec = vectors[i] if i < len(vectors) else []
            has_valid_vector = bool(vec and len(vec) > 0 and any(v != 0 for v in vec))

            processed_chunks.append({
                **chunk_data,
                "content_hash": hashes[i],
                "embedding": vec,
                "embedding_status": EmbeddingStatus.COMPLETED.value if has_valid_vector else EmbeddingStatus.FAILED.value,
            })

        logger.info(f"Generated embeddings for {len(processed_chunks)} chunks.")
        return processed_chunks

    except Exception as e:
        logger.error(f"Error in embedding generation service: {e}")
        # Return chunks marked FAILED
        return [
            {
                **c,
                "content_hash": hashes[i],
                "embedding": None,
                "embedding_status": EmbeddingStatus.FAILED.value,
            }
            for i, c in enumerate(chunks)
        ]
