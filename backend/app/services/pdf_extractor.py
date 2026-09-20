import os
from typing import Dict, Any, List
import pypdf


def extract_pdf_pages(file_path: str) -> Dict[str, Any]:
    """
    Extracts text page-by-page from a PDF file using pypdf.
    Preserves page numbers, text order, and metadata.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found at path: {file_path}")

    reader = pypdf.PdfReader(file_path)
    page_count = len(reader.pages)
    extracted_pages: List[Dict[str, Any]] = []

    for page_idx, page in enumerate(reader.pages):
        page_num = page_idx + 1
        raw_text = page.extract_text() or ""
        extracted_pages.append({
            "page_number": page_num,
            "text": raw_text
        })

    return {
        "page_count": page_count,
        "pages": extracted_pages
    }
