"""
Health check endpoint.
Returns service status and version.
Used by smoke tests, load balancers, and monitoring.
"""
from fastapi import APIRouter
from pydantic import BaseModel
import structlog

log = structlog.get_logger()
router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    Returns 200 when the service is running correctly.
    """
    log.info("health.check")
    return HealthResponse(
        status="ok",
        version="0.1.0",
        environment="development",
    )
