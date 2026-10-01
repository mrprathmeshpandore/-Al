import io
import os
from typing import Dict, Any, List, Union
import pypdf


def extract_pdf_pages(file_input: Union[str, bytes, io.BytesIO]) -> Dict[str, Any]:
    """
    Extracts text page-by-page from a PDF file (path or bytes) using pypdf.
    Preserves page numbers, text order, and metadata.
    """
    if isinstance(file_input, str):
        if not os.path.exists(file_input):
            raise FileNotFoundError(f"PDF file not found at path: {file_input}")
        reader = pypdf.PdfReader(file_input)
    elif isinstance(file_input, bytes):
        reader = pypdf.PdfReader(io.BytesIO(file_input))
    elif isinstance(file_input, io.BytesIO):
        reader = pypdf.PdfReader(file_input)
    else:
        raise ValueError("Unsupported PDF input type. Must be file path, bytes, or BytesIO.")

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
