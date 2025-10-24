"""Command-line helpers for backend maintenance tasks."""

from __future__ import annotations

from app.core.config import Settings


def check_environment() -> None:
    """Validate environment variables using the Settings schema."""

    try:
        Settings()
    except Exception as exc:  # pragma: no cover - defensive guard for CLI usage
        message = f"Environment validation failed: {exc}"
        raise SystemExit(message) from exc

    print("Environment configuration looks good.")


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    check_environment()
