"""Stateless OAuth state token generation and verification."""

from __future__ import annotations

import secrets
from datetime import timedelta

from itsdangerous import BadSignature, URLSafeTimedSerializer

from app.core.config import Settings


class OAuthStateError(RuntimeError):
    """Raised when OAuth state cannot be generated or validated."""


class OAuthStateManager:
    """Generate and validate signed OAuth state parameters."""

    def __init__(self, settings: Settings, ttl: timedelta | None = None) -> None:
        if not settings.session_secret:
            raise OAuthStateError("SESSION_SECRET is not configured")
        self._serializer = URLSafeTimedSerializer(secret_key=settings.session_secret)
        self._ttl = ttl or timedelta(minutes=10)

    def issue(self) -> str:
        """Return a new signed state token."""

        nonce = secrets.token_urlsafe(32)
        return self._serializer.dumps({"nonce": nonce})

    def verify(self, value: str) -> None:
        """Validate that the provided state token is well-formed."""

        try:
            self._serializer.loads(value, max_age=int(self._ttl.total_seconds()))
        except BadSignature as exc:  # pragma: no cover - indicates tampering
            raise OAuthStateError("Invalid or expired OAuth state parameter") from exc
