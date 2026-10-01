from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator


class AIAskRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="UPSC question or query string")
    top_k: Optional[int] = Field(default=None, ge=1, le=20, description="Optional maximum number of chunks to retrieve")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata filters (subject, topic, category)")

    @field_validator("query")
    @classmethod
    def validate_non_empty_query(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Query string must not be empty or whitespace only.")
        return clean


class CitationSchema(BaseModel):
    resource_id: str = Field(..., description="ID of the parent resource")
    resource_title: str = Field(..., description="Title of the parent resource")
    document_id: str = Field(..., description="ID of the document")
    page_number: Optional[int] = Field(None, description="Page number in PDF document")
    chunk_index: int = Field(..., description="Index of the chunk in the document")
    score: float = Field(..., description="Cosine similarity score of chunk")


class AIAskResponse(BaseModel):
    query: str = Field(..., description="Original user query string")
    answer: str = Field(..., description="Grounded answer text")
    grounded: bool = Field(..., description="True if answer is backed by retrieved sources")
    sources: List[CitationSchema] = Field(default_factory=list, description="Backend-verified citation metadata sources")
