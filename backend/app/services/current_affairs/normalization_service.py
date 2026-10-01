import re
import unicodedata
from datetime import datetime, timezone
from typing import Optional

from app.constants.current_affairs import VALID_CATEGORIES, CurrentAffairCategory
from app.services.current_affairs.base_source import CurrentAffairCandidate


class NormalizationService:
    """Service to clean, sanitize and normalize incoming current affair candidates."""

    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""
        # Strip HTML tags
        text = re.sub(r"<[^>]+>", " ", text)
        # Normalize unicode characters
        text = unicodedata.normalize("NFKC", text)
        # Replace multiple whitespace characters with single space
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @staticmethod
    def generate_slug(title: str) -> str:
        cleaned = NormalizationService.clean_text(title).lower()
        # Convert non-alphanumeric to hyphens
        slug = re.sub(r"[^\w\s-]", "", cleaned)
        slug = re.sub(r"[-\s]+", "-", slug).strip("-")
        return slug or "current-affair"

    @staticmethod
    def normalize_category(category: Optional[str]) -> str:
        if not category:
            return CurrentAffairCategory.NATIONAL.value
        cat_upper = category.strip().upper().replace(" ", "_").replace("&", "AND")
        if cat_upper in VALID_CATEGORIES:
            return cat_upper
        # Fuzzy fallback mapping
        if "GOVERN" in cat_upper or "ADMIN" in cat_upper:
            return CurrentAffairCategory.GOVERNANCE.value
        if "POLIT" in cat_upper or "CONSTITUT" in cat_upper:
            return CurrentAffairCategory.POLITY.value
        if "ECONOM" in cat_upper or "FINANC" in cat_upper or "BUDGET" in cat_upper:
            return CurrentAffairCategory.ECONOMY.value
        if "ENVIRON" in cat_upper or "CLIMATE" in cat_upper or "ECOL" in cat_upper:
            return CurrentAffairCategory.ENVIRONMENT.value
        if "SCIENCE" in cat_upper or "TECH" in cat_upper or "ISRO" in cat_upper:
            return CurrentAffairCategory.SCIENCE_TECHNOLOGY.value
        if "SECURITY" in cat_upper or "DEFENCE" in cat_upper:
            return CurrentAffairCategory.INTERNAL_SECURITY.value
        if "INTERNATIONAL" in cat_upper or "RELATION" in cat_upper or "DIPLOM" in cat_upper:
            return CurrentAffairCategory.INTERNATIONAL_RELATIONS.value
        if "ETHIC" in cat_upper:
            return CurrentAffairCategory.ETHICS.value
        if "SOCIAL" in cat_upper or "HEALTH" in cat_upper or "EDUCATION" in cat_upper:
            return CurrentAffairCategory.SOCIAL_ISSUES.value

        return CurrentAffairCategory.NATIONAL.value

    @staticmethod
    def normalize_candidate(candidate: CurrentAffairCandidate) -> CurrentAffairCandidate:
        cleaned_title = NormalizationService.clean_text(candidate.title)
        cleaned_content = NormalizationService.clean_text(candidate.content)
        cleaned_summary = NormalizationService.clean_text(candidate.summary) if candidate.summary else None
        norm_category = NormalizationService.normalize_category(candidate.category)

        pub_date = candidate.published_at
        if pub_date is not None:
            if pub_date.tzinfo is not None:
                pub_date = pub_date.astimezone(timezone.utc).replace(tzinfo=None)

        return CurrentAffairCandidate(
            title=cleaned_title,
            source_name=candidate.source_name.strip() if candidate.source_name else "Official Source",
            content=cleaned_content,
            source_url=candidate.source_url.strip() if candidate.source_url else None,
            published_at=pub_date,
            category=norm_category,
            topic=NormalizationService.clean_text(candidate.topic) if candidate.topic else None,
            subtopic=NormalizationService.clean_text(candidate.subtopic) if candidate.subtopic else None,
            summary=cleaned_summary,
            key_points=[NormalizationService.clean_text(kp) for kp in candidate.key_points if kp],
        )
