"""Healthcheck endpoints used by infrastructure probes."""

from fastapi import APIRouter

from app.schemas.health import HealthStatus

router = APIRouter(tags=["health"])


@router.get("/healthz", summary="Liveness probe", response_model=HealthStatus)
def healthcheck() -> HealthStatus:
    """Return a simple liveness status payload."""
    return HealthStatus(status="ok")


@router.get("/readyz", summary="Readiness probe", response_model=HealthStatus)
def readiness() -> HealthStatus:
    """Signal that the application is ready to receive traffic."""
    return HealthStatus(status="ready")
