"""Pydantic models describing realtime WebSocket payloads."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.runtime import FeatureFlags


class WebSocketHandshake(BaseModel):
    """Initial handshake frame emitted when a client connects."""

    type: Literal["handshake"] = "handshake"  # noqa: A003
    event_id: str
    mode: str
    heartbeat_sec: int
    server_time: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    feature_flags: FeatureFlags


class HeartbeatMessage(BaseModel):
    """Heartbeat frame allowing clients to detect stale connections."""

    type: Literal["heartbeat"] = "heartbeat"  # noqa: A003
    event_id: str
    server_time: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class GameDelta(BaseModel):
    """Delta payload describing a single play or scoreboard update."""

    event_id: str
    sequence: int
    clock: str | None = None
    quarter: int | None = Field(default=None, ge=1, le=5)
    down: int | None = Field(default=None, ge=1, le=4)
    distance: int | None = Field(default=None, ge=1)
    yardline_100: int | None = Field(default=None, ge=0, le=100)
    type: str = Field(alias="type", serialization_alias="type")  # noqa: A003
    yards: int | None = None
    flags: list[str] = Field(default_factory=list)
    description: str | None = None
    play_id: str | None = None
    source: Literal["pyespn"] = "pyespn"
    generated_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    replay: bool = False


class GameDeltaEnvelope(BaseModel):
    """Envelope describing a delta message sent to the client."""

    type: Literal["delta"] = "delta"  # noqa: A003
    event_id: str
    data: GameDelta


class ReplayCompleteMessage(BaseModel):
    """Sent when a replay stream has delivered all plays."""

    type: Literal["replay_complete"] = "replay_complete"  # noqa: A003
    event_id: str


class ErrorMessage(BaseModel):
    """Structured error payload for websocket interactions."""

    type: Literal["error"] = "error"  # noqa: A003
    event_id: str
    code: str
    message: str
