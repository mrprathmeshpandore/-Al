import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Resource(Base):
    __tablename__ = "resources"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, index=True)
    subject = Column(String(100), nullable=False, index=True)
    topic = Column(String(100), nullable=True, index=True)
    resource_type = Column(String(50), nullable=False, default="pdf", index=True)
    source = Column(String(255), nullable=True)
    is_official = Column(Boolean, default=False, nullable=False)

    created_by = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    documents = relationship("Document", back_populates="resource", cascade="all, delete-orphan")
    bookmarks = relationship("ResourceBookmark", back_populates="resource", cascade="all, delete-orphan")
    creator = relationship("User")
