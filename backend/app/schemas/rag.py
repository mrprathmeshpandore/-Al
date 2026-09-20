from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


class RAGSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query string for RAG knowledge retrieval")
    top_k: Optional[int] = Field(default=None, ge=1, le=20, description="Maximum number of relevant chunks to retrieve")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata filters (subject, category, topic, resource_id)")


class RAGSearchResultItem(BaseModel):
    chunk_id: str
    document_id: str
    resource_id: str
    resource_title: str
    content: str
    page_number: int
    chunk_index: int
    score: float
    source: Optional[str] = None
    subject: str
    topic: Optional[str] = None
    category: str
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class RAGSearchResponse(BaseModel):
    query: str
    results: List[RAGSearchResultItem] = []
    message: str
