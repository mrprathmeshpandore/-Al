from typing import List, Dict, Any


def chunk_pages(
    pages: List[Dict[str, Any]],
    chunk_size: int = 1000,
    chunk_overlap: int = 150
) -> List[Dict[str, Any]]:
    """
    Splits page-aware text into deterministic chunks with specified size and overlap.
    Preserves page number and chunk index.
    """
    chunks: List[Dict[str, Any]] = []
    global_chunk_idx = 0

    step = max(1, chunk_size - chunk_overlap)

    for page in pages:
        page_num = page.get("page_number", 1)
        text = page.get("text", "")

        if not text.strip():
            continue

        text_len = len(text)
        start = 0

        while start < text_len:
            end = min(start + chunk_size, text_len)
            
            # If not at text end, try to snap to nearest space boundary to avoid word splits
            if end < text_len:
                last_space = text.rfind(' ', start + int(chunk_size * 0.8), end)
                if last_space != -1 and last_space > start:
                    end = last_space

            chunk_content = text[start:end].strip()

            if chunk_content:
                word_count = len(chunk_content.split())
                chunks.append({
                    "chunk_index": global_chunk_idx,
                    "page_number": page_num,
                    "content": chunk_content,
                    "metadata": {
                        "char_length": len(chunk_content),
                        "word_count": word_count,
                        "page_number": page_num,
                    }
                })
                global_chunk_idx += 1

            if end >= text_len:
                break

            start = start + step

    return chunks
