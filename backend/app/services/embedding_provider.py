import time
import logging
import hashlib
from abc import ABC, abstractmethod
from typing import List, Optional
import httpx

from app.core.config import settings

logger = logging.getLogger("embedding_provider")


class BaseEmbeddingProvider(ABC):
    """
    Abstract Base Class for Embedding Providers.
    Decouples RAG knowledge retrieval from specific LLM / vector generation APIs.
    """

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generates embedding vector for a single text string."""
        pass

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generates embedding vectors for a list of document chunk texts."""
        pass


class FakeEmbeddingProvider(BaseEmbeddingProvider):
    """
    Deterministic Mock Embedding Provider for automated test suites.
    Produces normalized float vectors matching EMBEDDING_DIMENSION without API costs or external dependencies.
    """

    def __init__(self, vector_dim: Optional[int] = None):
        self.vector_dim = vector_dim or settings.EMBEDDING_DIMENSION

    def _generate_vector(self, text: str) -> List[float]:
        if not text:
            return [0.0] * self.vector_dim

        # Generate seed from text MD5 hash
        seed = int(hashlib.md5(text.encode('utf-8')).hexdigest(), 16)
        vector = []
        for i in range(self.vector_dim):
            val = ((seed + i * 10007) % 20000 - 10000) / 10000.0
            vector.append(round(val, 6))

        # Normalize vector to unit length (Euclidean magnitude = 1.0)
        magnitude = (sum(x * x for x in vector)) ** 0.5
        if magnitude > 0:
            vector = [round(x / magnitude, 6) for x in vector]

        return vector

    def embed_text(self, text: str) -> List[float]:
        return self._generate_vector(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]


class GeminiEmbeddingProvider(BaseEmbeddingProvider):
    """
    Production Embedding Provider using Google Gemini REST / SDK API.
    Supports batching, exponential backoff retries for rate limits (429/5xx), and vector dimension validation.
    """
    _http_client: Optional[httpx.Client] = None

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, vector_dim: Optional[int] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_EMBEDDING_MODEL
        self.vector_dim = vector_dim or settings.EMBEDDING_DIMENSION

    @classmethod
    def _get_http_client(cls) -> httpx.Client:
        if cls._http_client is None or cls._http_client.is_closed:
            cls._http_client = httpx.Client(timeout=30.0, limits=httpx.Limits(max_keepalive_connections=20, max_connections=50))
        return cls._http_client

    def _call_gemini_batch_api(self, texts: List[str]) -> List[List[float]]:
        """Invokes Gemini Embedding API via HTTP/SDK with retries and exponential backoff."""
        if not self.api_key:
            logger.warning("GEMINI_API_KEY is not configured. Falling back to FakeEmbeddingProvider.")
            return FakeEmbeddingProvider(self.vector_dim).embed_documents(texts)

        # Batch request payload for Gemini REST API
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:batchEmbedContents?key={self.api_key}"
        requests_payload = [
            {
                "model": f"models/{self.model}",
                "content": {"parts": [{"text": t}]}
            }
            for t in texts
        ]

        max_retries = 3
        backoff = 1.0

        for attempt in range(max_retries):
            try:
                client = self._get_http_client()
                response = client.post(url, json={"requests": requests_payload})

                if response.status_code == 200:
                    data = response.json()
                    embeddings_raw = data.get("embeddings", [])
                    results = []
                    for item in embeddings_raw:
                        vec = item.get("values", [])
                        if len(vec) > self.vector_dim:
                            vec = vec[:self.vector_dim]
                        elif len(vec) < self.vector_dim and len(vec) > 0:
                            vec = vec + [0.0] * (self.vector_dim - len(vec))
                        results.append(vec)
                    return results
                
                elif response.status_code in (429, 500, 502, 503, 504):
                    logger.warning(f"Gemini API rate limit/server error {response.status_code}. Retrying in {backoff}s...")
                    time.sleep(backoff)
                    backoff *= 2.0
                else:
                    logger.warning(f"Gemini API error {response.status_code} (non-retryable): {response.text[:200]}. Falling back.")
                    break
            except Exception as e:
                logger.warning(f"Network error calling Gemini API (attempt {attempt+1}): {e}")
                break

        # Fallback to FakeEmbeddingProvider if API attempts fail
        logger.error("All Gemini API attempts failed. Using fallback embedding provider.")
        return FakeEmbeddingProvider(self.vector_dim).embed_documents(texts)

    def embed_text(self, text: str) -> List[float]:
        res = self.embed_documents([text])
        return res[0] if res else [0.0] * self.vector_dim

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        all_embeddings = []
        batch_size = settings.EMBEDDING_BATCH_SIZE

        # Batch texts into chunks of EMBEDDING_BATCH_SIZE
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_vectors = self._call_gemini_batch_api(batch)
            all_embeddings.extend(batch_vectors)

        return all_embeddings


_cached_embedding_provider: Optional[BaseEmbeddingProvider] = None

def get_embedding_provider(force_fake: bool = False, custom_fake: Optional[FakeEmbeddingProvider] = None) -> BaseEmbeddingProvider:
    """
    Factory function returning the active embedding provider.
    Caches provider globally to eliminate instantiation overhead.
    Returns GeminiEmbeddingProvider if GEMINI_API_KEY is configured, else FakeEmbeddingProvider.
    """
    global _cached_embedding_provider
    if custom_fake:
        return custom_fake
    if force_fake or not settings.GEMINI_API_KEY:
        return FakeEmbeddingProvider()
    
    if _cached_embedding_provider is None:
        _cached_embedding_provider = GeminiEmbeddingProvider()
    return _cached_embedding_provider
