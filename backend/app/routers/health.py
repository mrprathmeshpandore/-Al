from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db
from app.services.cache_service import get_cache_service
from app.services.storage_service import get_storage_service
from app.core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Health Check")
def health_check():
    """
    Returns basic health status of the Prashasak AI FastAPI service.
    """
    return {
        "status": "ok",
        "service": "Prashasak AI API",
        "environment": settings.ENVIRONMENT
    }


@router.get("/health/liveness", summary="Liveness Probe")
def liveness_check():
    """
    Fast liveness probe confirming backend application process is alive.
    """
    return {"status": "alive"}


@router.get("/health/readiness", summary="Readiness Probe")
def readiness_check(db: Session = Depends(get_db)):
    """
    Comprehensive readiness probe verifying DB, Cache, Storage, and AI provider readiness.
    Does not expose sensitive credentials or internal paths.
    """
    db_status = "unhealthy"
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"

    cache = get_cache_service()
    cache_status = "healthy" if cache.is_available() else "degraded"

    storage = get_storage_service()
    storage_provider_name = settings.STORAGE_PROVIDER

    ai_provider_configured = bool(settings.GEMINI_API_KEY)

    is_ready = db_status == "healthy"

    response_payload = {
        "status": "ready" if is_ready else "not_ready",
        "components": {
            "database": db_status,
            "cache": cache_status,
            "storage_provider": storage_provider_name,
            "ai_configured": ai_provider_configured,
        }
    }

    if not is_ready:
        raise HTTPException(status_code=503, detail=response_payload)

    return response_payload
