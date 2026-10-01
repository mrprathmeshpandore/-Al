from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class CurrentAffairCandidate:
    title: str
    source_name: str
    content: str
    source_url: Optional[str] = None
    published_at: Optional[datetime] = None
    category: str = "NATIONAL"
    topic: Optional[str] = None
    subtopic: Optional[str] = None
    summary: Optional[str] = None
    key_points: List[str] = field(default_factory=list)


class BaseCurrentAffairsSource(ABC):
    """Abstract Base Class for pluggable current affairs sources."""

    def __init__(self, source_name: str):
        self.source_name = source_name

    @abstractmethod
    def fetch_latest(self, limit: int = 20) -> List[CurrentAffairCandidate]:
        """Fetch latest current affair candidates from this source."""
        pass
