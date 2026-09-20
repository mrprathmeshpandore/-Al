from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class DocumentResponse(BaseModel):
    id: str
    resource_id: str
    original_filename: str
    mime_type: str
    file_size: int
    page_count: int
    processing_status: str
    error_message: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResourceResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    category: str
    subject: str
    topic: Optional[str] = None
    resource_type: str
    source: Optional[str] = None
    is_official: bool
    created_by: str
    created_at: datetime
    updated_at: datetime
    is_bookmarked: bool = False
    documents: List[DocumentResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ResourceUploadResponse(BaseModel):
    resource_id: str
    document_id: str
    processing_status: str
    message: str


class CategorySummary(BaseModel):
    category: str
    resource_count: int


class SubjectSummary(BaseModel):
    subject: str
    resource_count: int


class BookmarkResponse(BaseModel):
    id: str
    resource_id: str
    user_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
