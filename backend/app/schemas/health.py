"""Schemas for health endpoints."""

from pydantic import BaseModel


class HealthStatus(BaseModel):
    """Simple status response."""

    status: str
