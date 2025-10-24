"""Runtime metadata schemas shared between REST and realtime surfaces."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class FeatureFlags(BaseModel):
    """Feature flag toggles surfaced to clients."""

    replay: bool
    weather: bool


class RuntimeConfigResponse(BaseModel):
    """Payload returned by the runtime configuration endpoint."""

    generated_at: datetime
    environment: str
    api_prefix: str
    heartbeat_sec: int
    feature_flags: FeatureFlags
    websocket_paths: dict[str, str]
