from abc import ABC, abstractmethod
from typing import List
import hashlib


class BaseEmbeddingProvider(ABC):
    """
    Abstract Base Class for Embedding Providers (Pluggable interface for Gemini Embeddings or local vector generation).
    """

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding vector for a single text string."""
        pass

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embedding vectors for a list of text strings."""
        pass


class DefaultEmbeddingProvider(BaseEmbeddingProvider):
    """
    Default embedding provider implementation that generates normalized 384-dimensional
    vector representations. Can be easily swapped with GeminiEmbeddingProvider in Phase 4.
    """

    def __init__(self, vector_dim: int = 384):
        self.vector_dim = vector_dim

    def _hash_to_vector(self, text: str) -> List[float]:
        """Generates a deterministic vector based on text hash for testing and development."""
        if not text:
            return [0.0] * self.vector_dim

        # Generate a seed from MD5 hash
        seed = int(hashlib.md5(text.encode('utf-8')).hexdigest(), 16)
        vector = []
        for i in range(self.vector_dim):
            val = ((seed + i * 10007) % 20000 - 10000) / 10000.0
            vector.append(round(val, 6))

        # Normalize vector magnitude
        magnitude = (sum(x * x for x in vector)) ** 0.5
        if magnitude > 0:
            vector = [round(x / magnitude, 6) for x in vector]

        return vector

    def embed_text(self, text: str) -> List[float]:
        return self._hash_to_vector(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]


def get_embedding_provider() -> BaseEmbeddingProvider:
    """Factory function returning the active embedding provider."""
    return DefaultEmbeddingProvider()
