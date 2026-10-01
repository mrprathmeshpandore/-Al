import time
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.services.cache_service import InMemoryCacheService, RedisCacheService, get_cache_service
from app.services.storage_service import LocalStorageService, S3StorageService, get_storage_service
from app.services.task_queue import LocalAsyncTaskQueue, CeleryTaskQueue, get_task_queue
from app.core.logging_config import StructuredJSONFormatter
from app.utils.retry import retry_with_backoff
from app.services.retrieval_service import compute_cosine_similarity

client = TestClient(app)


def test_cache_service_in_memory_hit_miss_and_ttl():
    """Verify InMemoryCacheService get, set, delete, and TTL purge behavior."""
    cache = InMemoryCacheService()
    cache.flush()

    # Cache miss
    assert cache.get("test_key") is None

    # Cache set & hit
    cache.set("test_key", {"data": 123}, ttl=60)
    cached_val = cache.get("test_key")
    assert cached_val == {"data": 123}

    # Delete pattern
    cache.set("user:1:profile", "prof1")
    cache.set("user:1:stats", "stat1")
    cache.delete_pattern("user:1:*")
    assert cache.get("user:1:profile") is None
    assert cache.get("user:1:stats") is None

    # TTL expiration
    cache.set("short_key", "val", ttl=1)
    time.sleep(1.1)
    assert cache.get("short_key") is None


def test_cache_service_redis_fallback():
    """Verify RedisCacheService gracefully handles unserviceable URLs without throwing errors."""
    redis_service = RedisCacheService("redis://localhost:9999/0")
    assert redis_service.is_available() is False
    assert redis_service.get("any_key") is None
    assert redis_service.set("any_key", "val") is False
    assert redis_service.delete("any_key") is False


def test_storage_service_local_save_get_delete(tmp_path):
    """Verify LocalStorageService file operations."""
    storage = LocalStorageService(base_dir=str(tmp_path))
    filename = "test_doc.pdf"
    content = b"%PDF-1.4 mock pdf content"

    path = storage.save_file(content, filename)
    assert storage.file_exists(filename) is True

    retrieved = storage.get_file(filename)
    assert retrieved == content

    assert storage.delete_file(filename) is True
    assert storage.file_exists(filename) is False


def test_storage_service_s3_fallback():
    """Verify S3StorageService falls back safely if unconfigured."""
    s3_storage = S3StorageService()
    filename = "s3_test.pdf"
    content = b"s3 mock bytes"

    # Should fall back gracefully to local storage
    path = s3_storage.save_file(content, filename)
    assert s3_storage.file_exists(filename) is True
    assert s3_storage.get_file(filename) == content
    assert s3_storage.delete_file(filename) is True


def test_task_queue_local_enqueue():
    """Verify LocalAsyncTaskQueue enqueues work asynchronously."""
    queue = get_task_queue()
    executed = []

    def sample_task(val):
        executed.append(val)

    res = queue.enqueue(sample_task, "test_item")
    assert res is True
    time.sleep(0.1)
    assert "test_item" in executed


def test_structured_json_logger_redaction():
    """Verify StructuredJSONFormatter redacts sensitive field values."""
    formatter = StructuredJSONFormatter()

    class MockRecord:
        levelname = "INFO"
        name = "test_logger"
        exc_info = None
        extra = {
            "user_id": "usr-123",
            "password": "secret_password_123",
            "api_key": "gemini_secret_key"
        }

        def getMessage(self):
            return "Test log message"

    formatted = formatter.format(MockRecord())
    assert "usr-123" in formatted
    assert "[REDACTED]" in formatted
    assert "secret_password_123" not in formatted
    assert "gemini_secret_key" not in formatted


def test_retry_utility_with_backoff():
    """Verify retry_with_backoff utility retries transient failures."""
    attempts = []

    def flaky_fn():
        attempts.append(1)
        if len(attempts) < 3:
            raise ValueError("Transient error")
        return "success"

    res = retry_with_backoff(
        flaky_fn,
        max_retries=3,
        initial_delay=0.01,
        retryable_exceptions=(ValueError,)
    )
    assert res == "success"
    assert len(attempts) == 3


def test_cosine_similarity_edge_cases():
    """Verify vector cosine similarity calculation performance and precision."""
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    assert compute_cosine_similarity(v1, v2) == 1.0

    v3 = [0.0, 1.0, 0.0]
    assert compute_cosine_similarity(v1, v3) == 0.0

    assert compute_cosine_similarity([], []) == 0.0


def test_correlation_id_and_process_time_middleware():
    """Verify X-Request-ID and X-Process-Time headers are attached to responses."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert "x-request-id" in response.headers
    assert "x-process-time" in response.headers
    assert response.headers["x-process-time"].endswith("ms")


def test_health_liveness_and_readiness_probes():
    """Verify /health/liveness and /health/readiness endpoints."""
    liveness_resp = client.get("/api/health/liveness")
    assert liveness_resp.status_code == 200
    assert liveness_resp.json() == {"status": "alive"}

    readiness_resp = client.get("/api/health/readiness")
    assert readiness_resp.status_code == 200
    data = readiness_resp.json()
    assert data["status"] == "ready"
    assert data["components"]["database"] == "healthy"
