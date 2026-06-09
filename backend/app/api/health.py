"""
Health check endpoints
"""
from fastapi import APIRouter
from app.utils.config import settings


router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    # Add checks for external dependencies (DB, S3, etc.)
    return {
        "status": "ready",
        "service": settings.app_name,
    }
