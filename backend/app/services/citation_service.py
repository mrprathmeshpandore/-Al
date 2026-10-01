import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("citation_service")


def build_backend_citations(
    retrieved_chunks: List[Dict[str, Any]],
    referenced_source_indexes: Optional[List[int]] = None
) -> List[Dict[str, Any]]:
    """
    Constructs citation metadata strictly from backend retrieved chunks.
    Disregards any model-generated citation text/metadata to prevent hallucinations.
    
    If referenced_source_indexes is provided (1-indexed), filters retrieved_chunks accordingly.
    Deduplicates identical chunk references while preserving similarity score.
    """
    if not retrieved_chunks:
        return []

    target_chunks = retrieved_chunks

    # If model provided valid 1-indexed source references, select those specific chunks
    if referenced_source_indexes:
        valid_indexes = {idx for idx in referenced_source_indexes if 1 <= idx <= len(retrieved_chunks)}
        if valid_indexes:
            target_chunks = [retrieved_chunks[idx - 1] for idx in sorted(valid_indexes)]

    citations = []
    seen = set()

    for chunk in target_chunks:
        res_id = str(chunk.get("resource_id", ""))
        doc_id = str(chunk.get("document_id", ""))
        page_num = chunk.get("page_number")
        chunk_idx = chunk.get("chunk_index", 0)
        title = chunk.get("resource_title", "Untitled Document")
        score = float(chunk.get("score", 0.0))

        dedup_key = (res_id, doc_id, page_num, chunk_idx)
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

        citations.append({
            "resource_id": res_id,
            "resource_title": title,
            "document_id": doc_id,
            "page_number": page_num,
            "chunk_index": chunk_idx,
            "score": round(score, 4),
        })

    return citations
