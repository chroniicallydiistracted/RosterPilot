"""Tests for the Settings configuration loader."""

from __future__ import annotations

import pytest

from app.core.config import Settings


@pytest.fixture(autouse=True)
def clear_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure environment-dependent caches do not bleed across tests."""

    for key in (
        "APP_ENV",
        "DATABASE_URL",
        "REDIS_URL",
        "SESSION_SECRET",
        "TOKEN_ENC_KEY",
        "YAHOO_CLIENT_ID",
        "YAHOO_CLIENT_SECRET",
        "YAHOO_REDIRECT_URI",
        "CORS_ALLOWED_ORIGINS",
    ):
        monkeypatch.delenv(key, raising=False)


def _set_required_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pass@localhost:5432/db")
    monkeypatch.setenv("REDIS_URL", "rediss://:token@localhost:6379/0")
    monkeypatch.setenv("SESSION_SECRET", "super-secret")
    monkeypatch.setenv("TOKEN_ENC_KEY", "encryption-key")
    monkeypatch.setenv("YAHOO_CLIENT_ID", "client-id")
    monkeypatch.setenv("YAHOO_CLIENT_SECRET", "client-secret")
    monkeypatch.setenv("YAHOO_REDIRECT_URI", "https://api.example.com/oauth/callback")


def test_settings_allows_local_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    """Local/test environments should not require production secrets."""

    monkeypatch.setenv("APP_ENV", "local")
    settings = Settings()

    assert settings.environment == "local"
    assert settings.database_url is None
    assert settings.cors_allowed_origins == []


def test_settings_parses_cors_list(monkeypatch: pytest.MonkeyPatch) -> None:
    """CORS origins should be parsed into a unique list."""

    _set_required_env(monkeypatch)
    monkeypatch.setenv(
        "CORS_ALLOWED_ORIGINS",
        "https://one.example, https://two.example ,https://one.example",
    )

    settings = Settings()

    assert settings.cors_allowed_origins == [
        "https://one.example",
        "https://two.example",
    ]


def test_settings_requires_secrets_in_production(monkeypatch: pytest.MonkeyPatch) -> None:
    """Missing required secrets in non-local environments should raise an error."""

    _set_required_env(monkeypatch)
    monkeypatch.delenv("YAHOO_CLIENT_SECRET")

    with pytest.raises(ValueError) as exc:
        Settings()

    assert "YAHOO_CLIENT_SECRET" in str(exc.value)
