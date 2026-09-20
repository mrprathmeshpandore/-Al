import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class ProcessingStatus(str, PyEnum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resource_id = Column(String(36), ForeignKey("resources.id", ondelete="CASCADE"), nullable=False, index=True)

    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False, unique=True)
    mime_type = Column(String(100), default="application/pdf", nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    page_count = Column(Integer, default=0, nullable=False)
    processing_status = Column(String(30), default=ProcessingStatus.UPLOADED.value, nullable=False, index=True)
    error_message = Column(Text, nullable=True)

    created_by = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    resource = relationship("Resource", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    creator = relationship("User")
