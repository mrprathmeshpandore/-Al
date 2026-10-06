import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.ai import AIAskRequest, AIAskResponse
from fastapi.responses import StreamingResponse
from app.services.rag_answer_service import generate_rag_grounded_answer, generate_rag_grounded_answer_stream

logger = logging.getLogger("ai_router")

router = APIRouter(
    prefix="/ai",
    tags=["AI Grounded Q&A"],
)


@router.post(
    "/ask",
    response_model=AIAskResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask AI a UPSC Question Grounded in Knowledge Base Resources",
    description="Retrieves relevant document chunks from the user's uploaded resource library, constructs a grounded context, and generates an answer using Google Gemini with backend-verified citation metadata.",
)
def ask_ai(
    payload: AIAskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    POST /api/ai/ask
    Authenticates user, performs RAG knowledge retrieval, and generates grounded Gemini answer with verified citations.
    """
    try:
        response_data = generate_rag_grounded_answer(
            query=payload.query,
            current_user_id=current_user.id,
            db=db,
            top_k=payload.top_k,
            filters=payload.filters,
        )
        return response_data
    except Exception as e:
        logger.error(f"Error in ask_ai endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your query."
        )


@router.post(
    "/ask/stream",
    status_code=status.HTTP_200_OK,
    summary="Stream AI Answer Grounded in Knowledge Base",
    description="Performs RAG retrieval and streams grounded Gemini answer text tokens in real time via Server-Sent Events (SSE).",
)
def ask_ai_stream(
    payload: AIAskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    POST /api/ai/ask/stream
    Streams AI grounded answer chunks using Server-Sent Events (SSE).
    First response metadata & token stream begins within ~2-3 seconds.
    """
    if not payload.query or not payload.query.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Search query cannot be empty"
        )

    try:
        generator = generate_rag_grounded_answer_stream(
            query=payload.query,
            current_user_id=current_user.id,
            db=db,
            top_k=payload.top_k,
            filters=payload.filters,
        )
        return StreamingResponse(
            generator,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )
    except Exception as e:
        logger.error(f"Error in ask_ai_stream endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while setting up answer stream."
        )
