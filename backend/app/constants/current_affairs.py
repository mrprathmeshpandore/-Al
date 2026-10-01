from enum import Enum
from typing import List


class CurrentAffairCategory(str, Enum):
    NATIONAL = "NATIONAL"
    INTERNATIONAL = "INTERNATIONAL"
    ECONOMY = "ECONOMY"
    GOVERNANCE = "GOVERNANCE"
    POLITY = "POLITY"
    ENVIRONMENT = "ENVIRONMENT"
    SCIENCE_TECHNOLOGY = "SCIENCE_TECHNOLOGY"
    SOCIAL_ISSUES = "SOCIAL_ISSUES"
    INTERNAL_SECURITY = "INTERNAL_SECURITY"
    ETHICS = "ETHICS"
    INTERNATIONAL_RELATIONS = "INTERNATIONAL_RELATIONS"


class AnalysisStatus(str, Enum):
    FETCHED = "FETCHED"
    NORMALIZED = "NORMALIZED"
    ANALYZING = "ANALYZING"
    ANALYZED = "ANALYZED"
    FAILED = "FAILED"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


VALID_CATEGORIES: List[str] = [category.value for category in CurrentAffairCategory]
VALID_STATUSES: List[str] = [status.value for status in AnalysisStatus]
