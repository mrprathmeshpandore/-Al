from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Health Check")
def health_check():
    """
    Returns the health status of the Prashasak AI FastAPI service.
    """
    return {
        "status": "ok",
        "service": "Prashasak AI API"
    }
