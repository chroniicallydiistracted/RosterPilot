"""Application configuration and environment management."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized configuration for the FastAPI service."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: Literal["local", "development", "staging", "production"] = "local"
    api_prefix: str = "/api"

    # Infrastructure providers
    database_url: str | None = None
    redis_url: str | None = None

    # Yahoo OAuth
    yahoo_client_id: str | None = None
    yahoo_client_secret: str | None = None
    yahoo_redirect_uri: str | None = None

    # Feature flags
    feature_weather: bool = False
    feature_replay: bool = True

    # Observability
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance for dependency injection."""
    return Settings()
