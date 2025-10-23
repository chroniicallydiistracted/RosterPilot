"""FastAPI dependency providers for application settings."""

from app.core.config import Settings, get_settings


def provide_settings() -> Settings:
    """Expose application settings for injection into routes and services."""
    return get_settings()
