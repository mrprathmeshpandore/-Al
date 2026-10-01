import logging
from typing import Dict, Any, Optional
from app.models.profile import UserProfile

logger = logging.getLogger("daf_context_builder")

VALID_PERSONALIZATION_SOURCES = {
    "EDUCATION",
    "HOMETOWN",
    "CURRENT_CITY",
    "OPTIONAL_SUBJECT",
    "UPSC_JOURNEY",
    "HOBBY",
    "SPORT",
    "BOOK",
    "INTEREST",
    "SOCIAL_ACTIVITY",
    "PERSPECTIVE",
    "WORK_EXPERIENCE",
    "GENERAL_DAF",
}


def _safe_get(data: Optional[Dict[str, Any]], *keys: str) -> Optional[str]:
    """Helper to extract non-empty string value from nested dictionary or profile attributes."""
    if not data or not isinstance(data, dict):
        return None
    for k in keys:
        val = data.get(k)
        if val is not None:
            if isinstance(val, str) and val.strip():
                return val.strip()
            if isinstance(val, list):
                non_empty = [str(x).strip() for x in val if x is not None and str(x).strip()]
                if non_empty:
                    return ", ".join(non_empty)
            if isinstance(val, (int, float, bool)):
                return str(val)
    return None


def extract_daf_topic_and_context(
    profile: Optional[Any] = None,
    source_type: Optional[Any] = None,
    **kwargs
) -> Optional[Dict[str, Any]]:
    """
    Reads candidate's UserProfile, extracts requested DAF field data,
    and constructs a structured DAF context block along with a focused topic query.
    
    Returns None if profile is missing or requested DAF source has no non-empty user value.
    """
    actual_profile = None
    actual_source = "GENERAL_DAF"

    if isinstance(profile, UserProfile):
        actual_profile = profile
        if isinstance(source_type, str):
            actual_source = source_type
    elif isinstance(source_type, UserProfile):
        actual_profile = source_type
        if isinstance(profile, str):
            actual_source = profile
    elif isinstance(profile, str):
        actual_source = profile
        if isinstance(source_type, UserProfile):
            actual_profile = source_type

    if not actual_profile:
        return None

    src = actual_source.upper().strip() if actual_source else "GENERAL_DAF"
    if src not in VALID_PERSONALIZATION_SOURCES:
        logger.warning(f"Invalid personalization source type: {src}")
        return None

    edu = profile.education_data or {}
    journey = profile.upsc_journey_data or {}
    interests = profile.interests or {}
    perspective = profile.perspective or {}

    daf_lines = []
    topic_query = ""
    label = ""
    subject_hint = "Governance"

    if src == "EDUCATION":
        deg = _safe_get(edu, "degree", "graduation")
        spec = _safe_get(edu, "specialization")
        univ = _safe_get(edu, "university")
        pg = _safe_get(edu, "postGraduation")
        other = _safe_get(edu, "otherQualifications")

        parts = [p for p in [deg, spec, pg, other] if p]
        if not parts and not univ:
            return None

        label = spec or deg or pg or other or "Higher Education"
        daf_lines.append("CANDIDATE DAF - EDUCATION:")
        if deg:
            daf_lines.append(f"- Graduation Degree: {deg}")
        if spec:
            daf_lines.append(f"- Specialization: {spec}")
        if univ:
            daf_lines.append(f"- University: {univ}")
        if pg:
            daf_lines.append(f"- Post Graduation: {pg}")
        if other:
            daf_lines.append(f"- Other Qualifications: {other}")

        topic_query = f"{label} technology public policy governance administration"
        subject_hint = "Education & Expertise"

    elif src == "HOMETOWN":
        state = profile.home_state or ""
        dist = profile.district or ""
        if not state and not dist:
            return None

        label = f"{dist}, {state}".strip(", ") if (dist and state) else (dist or state)
        daf_lines.append("CANDIDATE DAF - HOMETOWN / ORIGIN:")
        if dist:
            daf_lines.append(f"- Home District: {dist}")
        if state:
            daf_lines.append(f"- Home State: {state}")

        topic_query = f"{label} regional development governance administration socio-economic challenge"
        subject_hint = "Regional Administration"

    elif src == "CURRENT_CITY":
        city = profile.current_city or ""
        if not city.strip():
            return None

        label = city.strip()
        daf_lines.append("CANDIDATE DAF - CURRENT CITY:")
        daf_lines.append(f"- Current City: {label}")
        if profile.home_state:
            daf_lines.append(f"- Home State: {profile.home_state}")

        topic_query = f"{label} urban governance administration infrastructure public service"
        subject_hint = "Urban Governance"

    elif src == "OPTIONAL_SUBJECT":
        opt = _safe_get(journey, "optionalSubject", "optional")
        if not opt:
            return None

        label = opt
        daf_lines.append("CANDIDATE DAF - UPSC OPTIONAL SUBJECT:")
        daf_lines.append(f"- Optional Subject: {label}")
        if _safe_get(journey, "preparationStage"):
            daf_lines.append(f"- Preparation Stage: {_safe_get(journey, 'preparationStage')}")

        topic_query = f"{label} public administration governance civil service application"
        subject_hint = label

    elif src == "UPSC_JOURNEY":
        attempts = _safe_get(journey, "attemptCount", "attempts")
        stage = _safe_get(journey, "preparationStage")
        exp = _safe_get(journey, "previousInterviewExp")
        opt = _safe_get(journey, "optionalSubject")

        if not attempts and not stage and not exp and not opt:
            return None

        label = f"Attempt {attempts}" if attempts else (stage or "UPSC Preparation Journey")
        daf_lines.append("CANDIDATE DAF - UPSC PREPARATION JOURNEY:")
        if attempts:
            daf_lines.append(f"- Attempt Count: {attempts}")
        if stage:
            daf_lines.append(f"- Preparation Stage: {stage}")
        if exp:
            daf_lines.append(f"- Previous Interview Experience: {exp}")
        if opt:
            daf_lines.append(f"- Optional Subject: {opt}")

        topic_query = f"civil services preparation interview strategy public administration perspective {label}"
        subject_hint = "UPSC Journey"

    elif src == "HOBBY":
        hobby = _safe_get(interests, "hobbies", "hobby")
        if not hobby:
            return None

        label = hobby
        daf_lines.append("CANDIDATE DAF - HOBBIES & CREATIVE PURSUITS:")
        daf_lines.append(f"- Hobby: {label}")

        topic_query = f"{label} public administration leadership ethics society communication"
        subject_hint = "Hobbies & Interests"

    elif src == "SPORT":
        sport = _safe_get(interests, "sports", "sport")
        if not sport:
            return None

        label = sport
        daf_lines.append("CANDIDATE DAF - SPORTS & ATHLETICS:")
        daf_lines.append(f"- Sport: {label}")

        topic_query = f"{label} sports governance teamwork leadership sports policy public health"
        subject_hint = "Sports & Youth Affairs"

    elif src == "BOOK":
        books = _safe_get(interests, "readingBooks", "books")
        if not books:
            return None

        label = books
        daf_lines.append("CANDIDATE DAF - READING & LITERATURE:")
        daf_lines.append(f"- Favorite Books / Reading: {label}")

        topic_query = f"{label} literature ethics philosophy governance societal perspective"
        subject_hint = "Literature & Philosophy"

    elif src == "INTEREST":
        area = _safe_get(interests, "areasOfInterest", "interests")
        if not area:
            return None

        label = area
        daf_lines.append("CANDIDATE DAF - AREAS OF INTEREST:")
        daf_lines.append(f"- Area of Interest: {label}")

        topic_query = f"{label} public policy administration governance innovation"
        subject_hint = "Special Interest"

    elif src == "SOCIAL_ACTIVITY":
        social = _safe_get(interests, "socialActivities", "communityWork")
        if not social:
            return None

        label = social
        daf_lines.append("CANDIDATE DAF - SOCIAL & COMMUNITY ACTIVITIES:")
        daf_lines.append(f"- Social / Community Activity: {label}")

        topic_query = f"{label} social welfare community development public administration non-profit governance"
        subject_hint = "Social Welfare"

    elif src == "PERSPECTIVE":
        why = _safe_get(perspective, "whyCivilServices")
        focus = _safe_get(perspective, "keyFocusAreas")
        msg = _safe_get(perspective, "boardMessage")

        if not why and not focus and not msg:
            return None

        label = focus or "Civil Services Motivation"
        daf_lines.append("CANDIDATE DAF - PERSONAL PERSPECTIVE & MOTIVATION:")
        if why:
            daf_lines.append(f"- Motivation for Civil Services: {why}")
        if focus:
            daf_lines.append(f"- Key Focus Areas: {focus}")
        if msg:
            daf_lines.append(f"- Statement for Interview Board: {msg}")

        topic_query = f"{label} civil services motivation administrative ethics public service accountability"
        subject_hint = "Administrative Ethics"

    elif src == "WORK_EXPERIENCE":
        other_qual = _safe_get(edu, "workExperience", "otherQualifications", "work_experience")
        pg_qual = _safe_get(edu, "postGraduation")
        if not other_qual and not pg_qual:
            return None

        label = other_qual or pg_qual or "Professional Background"
        daf_lines.append("CANDIDATE DAF - PROFESSIONAL / WORK EXPERIENCE:")
        if other_qual:
            daf_lines.append(f"- Professional Experience / Qualification: {other_qual}")
        if pg_qual:
            daf_lines.append(f"- Higher Specialization: {pg_qual}")

        topic_query = f"{label} public administration professional experience governance policy"
        subject_hint = "Professional Experience"

    elif src == "GENERAL_DAF":
        # Consolidate all available non-empty profile elements
        deg = _safe_get(edu, "degree", "graduation")
        spec = _safe_get(edu, "specialization")
        univ = _safe_get(edu, "university")
        opt = _safe_get(journey, "optionalSubject")
        hobby = _safe_get(interests, "hobbies")
        why = _safe_get(perspective, "whyCivilServices")

        has_any = any([deg, spec, univ, opt, hobby, why, profile.home_state, profile.district])
        if not has_any:
            return None

        label = spec or deg or opt or hobby or profile.home_state or "General DAF Profile"
        daf_lines.append("CANDIDATE DAF SUMMARY:")
        if deg or spec or univ:
            edu_str = f"{deg or ''} ({spec or 'General'})".strip()
            if univ:
                edu_str += f" from {univ}"
            daf_lines.append(f"- Education: {edu_str}")
        if opt:
            daf_lines.append(f"- Optional Subject: {opt}")
        if profile.home_state or profile.district:
            daf_lines.append(f"- Origin: {profile.district or ''}, {profile.home_state or ''}".strip(", "))
        if hobby:
            daf_lines.append(f"- Hobby: {hobby}")
        if why:
            daf_lines.append(f"- Civil Services Perspective: {why}")

        topic_query = f"{label} civil services governance public administration ethics"
        subject_hint = "General DAF"

    daf_context_str = "\n".join(daf_lines)

    return {
        "daf_context": daf_context_str,
        "daf_context_str": daf_context_str,
        "topic_query": topic_query,
        "label": label,
        "subject_hint": subject_hint,
    }
