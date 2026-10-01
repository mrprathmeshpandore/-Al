import re
import logging
from typing import Tuple, Dict, Any

logger = logging.getLogger("question_validation_service")

PROHIBITED_PHRASES = [
    r"will be asked in upsc",
    r"definitely ask",
    r"guaranteed upsc",
    r"100% expected",
    r"confirmed upsc question",
    r"official upsc question",
    r"exact question in upsc",
]


def validate_generated_question(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validates a generated interview practice question dictionary.
    Verifies length bounds, required fields, structural integrity,
    and strict UPSC terminology compliance.
    """
    if not isinstance(data, dict):
        return False, "Generated question data is not a valid JSON dictionary."

    question_text = str(data.get("question", "")).strip()
    why_this_matters = str(data.get("why_this_matters", "")).strip()

    # 1. Question text presence and length checks
    if not question_text:
        return False, "Generated question text is empty."

    if len(question_text) < 15:
        return False, f"Generated question text is excessively short ({len(question_text)} chars)."

    if len(question_text) > 500:
        return False, f"Generated question text is excessively long ({len(question_text)} chars)."

    # 2. Context significance check
    if not why_this_matters:
        return False, "Generated question is missing 'why_this_matters' significance context."

    # 3. Prohibited terminology compliance checks
    lower_text = (question_text + " " + why_this_matters).lower()
    for pattern in PROHIBITED_PHRASES:
        if re.search(pattern, lower_text):
            logger.warning(f"Question rejected due to prohibited phrase matching pattern '{pattern}'.")
            return False, f"Question contains prohibited misleading terminology matching pattern '{pattern}'."

    return True, "Valid"
