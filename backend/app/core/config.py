"""Application configuration and environment management."""

from functools import lru_cache
from typing import ClassVar, Literal

from pydantic import Field, PrivateAttr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized configuration for the FastAPI service."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="",
        case_sensitive=False,
    )

    REQUIRED_IN_NON_LOCAL: ClassVar[tuple[str, ...]] = (
        "database_url",
        "redis_url",
        "session_secret",
        "token_enc_key",
        "yahoo_client_id",
        "yahoo_client_secret",
        "yahoo_redirect_uri",
    )

    _cors_allowed_origins: list[str] = PrivateAttr(default_factory=list)

    environment: Literal["local", "development", "staging", "production", "test"] = Field(
        default="local", alias="APP_ENV"
    )
    api_prefix: str = Field(default="/api")
    app_base_url: str | None = Field(default=None, alias="APP_BASE_URL")
    api_base_url: str | None = Field(default=None, alias="API_BASE_URL")

    # Infrastructure providers
    database_url: str | None = Field(default=None, alias="DATABASE_URL")
    redis_url: str | None = Field(default=None, alias="REDIS_URL")

    # Session & cookies
    session_secret: str | None = Field(default=None, alias="SESSION_SECRET")
    token_enc_key: str | None = Field(default=None, alias="TOKEN_ENC_KEY")
    cookie_domain: str | None = Field(default=None, alias="COOKIE_DOMAIN")
    cookie_secure: bool = Field(default=True, alias="COOKIE_SECURE")

    cors_allowed_origins_raw: str | None = Field(default=None, alias="CORS_ALLOWED_ORIGINS")

    # Yahoo OAuth
    yahoo_client_id: str | None = Field(default=None, alias="YAHOO_CLIENT_ID")
    yahoo_client_secret: str | None = Field(default=None, alias="YAHOO_CLIENT_SECRET")
    yahoo_redirect_uri: str | None = Field(default=None, alias="YAHOO_REDIRECT_URI")
    yahoo_scope: str = Field(default="fspt-r", alias="YAHOO_SCOPE")

    # Feature flags
    feature_weather: bool = Field(default=False, alias="FEATURE_WEATHER")
    feature_replay: bool = Field(default=True, alias="FEATURE_REPLAY")

    # Limits & caching
    cache_ttl_default: int = Field(default=300, alias="CACHE_TTL_DEFAULT")
    rate_limit_window: int = Field(default=60, alias="RATE_LIMIT_WINDOW")
    rate_limit_max: int = Field(default=120, alias="RATE_LIMIT_MAX")
    ws_heartbeat_sec: int = Field(default=25, alias="WS_HEARTBEAT_SEC")

    # Observability
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", alias="LOG_LEVEL"
    )
    otel_exporter_otlp_endpoint: str | None = Field(default=None, alias="OTEL_EXPORTER_OTLP_ENDPOINT")
    otel_exporter_otlp_headers: str | None = Field(default=None, alias="OTEL_EXPORTER_OTLP_HEADERS")
    sentry_dsn: str | None = Field(default=None, alias="SENTRY_DSN")

    timezone: str | None = Field(default=None, alias="TZ")

    @property
    def cors_allowed_origins(self) -> list[str]:
        """Return the configured CORS origins as a list."""

        return self._cors_allowed_origins

    @field_validator("cors_allowed_origins_raw")
    @classmethod
    def _split_cors_origins(cls, value: str | None) -> str | None:
        """Normalize whitespace for downstream parsing."""

        if value is None:
            return None
        return ",".join(part.strip() for part in value.split(",") if part.strip()) or None

    @model_validator(mode="after")
    def _finalize(self) -> "Settings":
        """Perform derived value computation and required-field validation."""

        origins_source = self.cors_allowed_origins_raw or ""
        self._cors_allowed_origins = [origin for origin in origins_source.split(",") if origin]

        if self.environment not in {"local", "test"}:
            missing = [
                field_name
                for field_name in self.REQUIRED_IN_NON_LOCAL
                if getattr(self, field_name) in {None, ""}
            ]
            if missing:
                env_names = [self.model_fields[field].alias or field for field in missing]
                joined = ", ".join(env_names)
                raise ValueError(f"Missing required environment variables: {joined}")

        self._cors_allowed_origins = list(dict.fromkeys(self._cors_allowed_origins))
        return self


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance for dependency injection."""

    return Settings()
