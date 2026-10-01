from typing import List
from app.services.current_affairs.base_source import BaseCurrentAffairsSource, CurrentAffairCandidate


class ManualCurrentAffairsSource(BaseCurrentAffairsSource):
    """Source provider for manually supplied/admin current affair candidates."""

    def __init__(self, candidates: List[CurrentAffairCandidate], source_name: str = "PIB / Official Press Releases"):
        super().__init__(source_name=source_name)
        self.candidates = candidates

    def fetch_latest(self, limit: int = 20) -> List[CurrentAffairCandidate]:
        return self.candidates[:limit]
