"""Shared service-layer data structures used across stub implementations."""

from __future__ import annotations

from dataclasses import dataclass
import uuid


@dataclass(slots=True)
class AuthContext:
    """Minimal representation of an authenticated Yahoo user."""

    user_id: uuid.UUID
    yahoo_sub: str
    scopes: list[str]
