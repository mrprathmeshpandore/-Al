import difflib
from typing import Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.current_affair import CurrentAffair
from app.services.current_affairs.normalization_service import NormalizationService


class DeduplicationService:
    """Service to detect and eliminate duplicate current affair items."""

    def __init__(self, db: Session, similarity_threshold: float = settings.CURRENT_AFFAIRS_DEDUP_SIMILARITY):
        self.db = db
        self.similarity_threshold = similarity_threshold

    def is_duplicate(self, title: str, source_url: Optional[str] = None, slug: Optional[str] = None) -> bool:
        return self.find_existing_duplicate(title=title, source_url=source_url, slug=slug) is not None

    def find_existing_duplicate(
        self, title: str, source_url: Optional[str] = None, slug: Optional[str] = None
    ) -> Optional[CurrentAffair]:
        # 1. Canonical URL match
        if source_url and source_url.strip():
            existing_by_url = (
                self.db.query(CurrentAffair)
                .filter(CurrentAffair.source_url == source_url.strip())
                .first()
            )
            if existing_by_url:
                return existing_by_url

        # 2. Slug / Normalized Title match
        target_slug = slug or NormalizationService.generate_slug(title)
        existing_by_slug = (
            self.db.query(CurrentAffair)
            .filter(CurrentAffair.slug == target_slug)
            .first()
        )
        if existing_by_slug:
            return existing_by_slug

        # 3. Normalized title similarity check against existing items
        clean_target_title = NormalizationService.clean_text(title).lower()

        # Query recent current affairs for comparison
        recent_affairs = (
            self.db.query(CurrentAffair)
            .order_by(CurrentAffair.created_at.desc())
            .limit(100)
            .all()
        )

        for affair in recent_affairs:
            existing_title = NormalizationService.clean_text(affair.title).lower()
            ratio = difflib.SequenceMatcher(None, clean_target_title, existing_title).ratio()
            if ratio >= self.similarity_threshold:
                return affair

        return None
