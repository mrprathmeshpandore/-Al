import re


def clean_text(text: str) -> str:
    """
    Cleans extracted PDF text:
    - Removes control/null characters
    - Fixes hyphenated line breaks (e.g. "gov-\nernance" -> "governance")
    - Normalizes consecutive spaces and line breaks
    """
    if not text:
        return ""

    # Remove null characters & control codes
    cleaned = text.replace("\x00", "")

    # Fix hyphenated words broken across lines
    cleaned = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', cleaned)

    # Normalize multiple newlines/spaces
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

    return cleaned.strip()
