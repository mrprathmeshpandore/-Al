import logging
from typing import List, Dict, Any

logger = logging.getLogger("context_builder")

MAX_CONTEXT_CHARACTERS = 12000


def build_rag_context(retrieved_chunks: List[Dict[str, Any]]) -> str:
    """
    Builds a structured, clean context block from retrieved RAG chunks.
    Preserves resource metadata (title, subject, page_number, chunk_index)
    while stripping raw vectors and internal database primary keys.
    """
    if not retrieved_chunks:
        return ""

    context_blocks = []
    total_length = 0

    for i, chunk in enumerate(retrieved_chunks, start=1):
        resource_title = chunk.get("resource_title", "Untitled Resource")
        subject = chunk.get("subject", "General")
        category = chunk.get("category", "")
        topic = chunk.get("topic", "")
        page_number = chunk.get("page_number", "N/A")
        chunk_index = chunk.get("chunk_index", "N/A")
        content = chunk.get("content", "").strip()

        header_lines = [f"[SOURCE {i}]", f"Title: {resource_title}"]
        if subject:
            header_lines.append(f"Subject: {subject}")
        if category:
            header_lines.append(f"Category: {category}")
        if topic:
            header_lines.append(f"Topic: {topic}")
        header_lines.append(f"Page: {page_number}")
        header_lines.append(f"Chunk Index: {chunk_index}")

        block_header = "\n".join(header_lines)
        block = f"{block_header}\n\nContent:\n{content}\n"

        # Enforce maximum context size bound
        if total_length + len(block) > MAX_CONTEXT_CHARACTERS:
            logger.warning(f"Context builder reached max character limit ({MAX_CONTEXT_CHARACTERS}). Truncating further chunks.")
            break

        context_blocks.append(block)
        total_length += len(block)

    return "\n---\n\n".join(context_blocks)
