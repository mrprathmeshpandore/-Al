import uuid
from enum import Enum as PyEnum
from sqlalchemy import Column, String, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class EmbeddingStatus(str, PyEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)

    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=False, default=1)
    content = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=True, index=True)
    chunk_metadata = Column(JSON, nullable=True)
    embedding = Column(JSON, nullable=True)  # Stores embedding vector floats [0.012, -0.045, ...]
    embedding_status = Column(String(30), default=EmbeddingStatus.PENDING.value, nullable=False, index=True)

    # Relationship
    document = relationship("Document", back_populates="chunks")
