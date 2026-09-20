import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class ResourceBookmark(Base):
    __tablename__ = "resource_bookmarks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resource_id = Column(String(36), ForeignKey("resources.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("resource_id", "user_id", name="uq_resource_user_bookmark"),
    )

    # Relationships
    resource = relationship("Resource", back_populates="bookmarks")
    user = relationship("User")
