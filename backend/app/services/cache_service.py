import json
import logging
import threading
import time
from abc import ABC, abstractmethod
from typing import Any, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class BaseCacheService(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from the cache by key."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in the cache with an optional TTL in seconds."""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete a key from the cache."""
        pass

    @abstractmethod
    def delete_pattern(self, pattern: str) -> bool:
        """Delete all keys matching a pattern (e.g. user:123:*)."""
        pass

    @abstractmethod
    def flush(self) -> bool:
        """Clear all cached keys."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if cache backend is operational."""
        pass


class InMemoryCacheService(BaseCacheService):
    """
    Thread-safe in-memory cache implementation with TTL support.
    Used as primary fallback when Redis is not configured or unavailable.
    """

    def __init__(self):
        self._store = {}
        self._lock = threading.RLock()

    def _purge_expired(self):
        now = time.time()
        expired_keys = [
            k for k, (val, exp) in self._store.items()
            if exp is not None and exp < now
        ]
        for k in expired_keys:
            self._store.pop(k, None)

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            self._purge_expired()
            item = self._store.get(key)
            if not item:
                return None
            val, exp = item
            if exp is not None and time.time() > exp:
                self._store.pop(key, None)
                return None
            return val

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        ttl = ttl if ttl is not None else settings.CACHE_TTL_SECONDS
        exp = time.time() + ttl if ttl and ttl > 0 else None
        with self._lock:
            self._purge_expired()
            self._store[key] = (value, exp)
            return True

    def delete(self, key: str) -> bool:
        with self._lock:
            return self._store.pop(key, None) is not None

    def delete_pattern(self, pattern: str) -> bool:
        with self._lock:
            # Simple wildcard prefix matching
            prefix = pattern.replace("*", "")
            keys_to_delete = [k for k in self._store if k.startswith(prefix)]
            for k in keys_to_delete:
                self._store.pop(k, None)
            return True

    def flush(self) -> bool:
        with self._lock:
            self._store.clear()
            return True

    def is_available(self) -> bool:
        return True


class RedisCacheService(BaseCacheService):
    """
    Redis cache service implementation.
    Gracefully degrades on connection failures.
    """

    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._client = None
        self._connect()

    def _connect(self):
        try:
            import redis
            self._client = redis.Redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_timeout=2.0,
                socket_connect_timeout=2.0,
            )
            self._client.ping()
            logger.info("Connected to Redis cache successfully.")
        except Exception as e:
            logger.warning(f"Redis cache connection failed ({e}). Falling back to memory mode.")
            self._client = None

    def is_available(self) -> bool:
        if not self._client:
            return False
        try:
            return bool(self._client.ping())
        except Exception:
            return False

    def get(self, key: str) -> Optional[Any]:
        if not self._client:
            return None
        try:
            data = self._client.get(key)
            if data is None:
                return None
            try:
                return json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return data
        except Exception as e:
            logger.warning(f"Redis get error for key '{key}': {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        if not self._client:
            return False
        ttl = ttl if ttl is not None else settings.CACHE_TTL_SECONDS
        try:
            serialized = json.dumps(value) if not isinstance(value, str) else value
            if ttl and ttl > 0:
                self._client.setex(key, ttl, serialized)
            else:
                self._client.set(key, serialized)
            return True
        except Exception as e:
            logger.warning(f"Redis set error for key '{key}': {e}")
            return False

    def delete(self, key: str) -> bool:
        if not self._client:
            return False
        try:
            return bool(self._client.delete(key))
        except Exception as e:
            logger.warning(f"Redis delete error for key '{key}': {e}")
            return False

    def delete_pattern(self, pattern: str) -> bool:
        if not self._client:
            return False
        try:
            keys = self._client.keys(pattern)
            if keys:
                self._client.delete(*keys)
            return True
        except Exception as e:
            logger.warning(f"Redis delete_pattern error for '{pattern}': {e}")
            return False

    def flush(self) -> bool:
        if not self._client:
            return False
        try:
            self._client.flushdb()
            return True
        except Exception as e:
            logger.warning(f"Redis flush error: {e}")
            return False


_cache_instance: Optional[BaseCacheService] = None


def get_cache_service() -> BaseCacheService:
    """
    Singleton factory for cache service.
    Returns RedisCacheService if REDIS_URL is configured and functional,
    otherwise returns InMemoryCacheService.
    """
    global _cache_instance
    if _cache_instance is not None:
        return _cache_instance

    if settings.REDIS_URL and settings.REDIS_URL.strip():
        redis_service = RedisCacheService(settings.REDIS_URL.strip())
        if redis_service.is_available():
            _cache_instance = redis_service
            return _cache_instance

    _cache_instance = InMemoryCacheService()
    return _cache_instance
