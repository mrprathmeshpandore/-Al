from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.rag import RAGSearchRequest, RAGSearchResponse
from app.services.retrieval_service import search_knowledge_base

router = APIRouter(prefix="/rag", tags=["RAG Knowledge Retrieval Engine"])


@router.post("/search", response_model=RAGSearchResponse)
def search_knowledge(
    payload: RAGSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    RAG Search Endpoint:
    Performs vector similarity search on uploaded PDF document knowledge base and returns top-K relevant chunks with citation metadata.
    """
    if not payload.query or not payload.query.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Search query cannot be empty"
        )

    response_data = search_knowledge_base(
        query=payload.query,
        top_k=payload.top_k,
        filters=payload.filters,
        current_user_id=current_user.id,
        db=db
    )

    return response_data
