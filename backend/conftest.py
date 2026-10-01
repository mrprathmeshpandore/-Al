import pytest
from app.core.config import settings


@pytest.fixture(autouse=True)
def force_testing_environment():
    """
    Autouse fixture for pytest suite:
    Ensures unit and integration tests use FakeGeminiService and FakeEmbeddingProvider
    by temporarily setting GEMINI_API_KEY to empty during test runs.
    """
    original_key = settings.GEMINI_API_KEY
    settings.GEMINI_API_KEY = ""
    yield
    settings.GEMINI_API_KEY = original_key
