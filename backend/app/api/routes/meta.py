"""Metadata endpoints exposing runtime configuration for clients."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import Settings
from app.dependencies.settings import provide_settings
from app.schemas.runtime import FeatureFlags, RuntimeConfigResponse

router = APIRouter(prefix="/meta", tags=["meta"])

SettingsDep = Annotated[Settings, Depends(provide_settings)]


@router.get("/config", response_model=RuntimeConfigResponse, summary="Runtime configuration")
async def get_runtime_configuration(settings: SettingsDep) -> RuntimeConfigResponse:
    """Return environment-aware configuration metadata for frontend clients."""

    feature_flags = FeatureFlags(
        replay=settings.feature_replay,
        weather=settings.feature_weather,
    )
    websocket_paths = {"game_updates": "/ws/games/{event_id}"}

    return RuntimeConfigResponse(
        generated_at=datetime.now(tz=UTC),
        environment=settings.environment,
        api_prefix=settings.api_prefix,
        heartbeat_sec=settings.ws_heartbeat_sec,
        feature_flags=feature_flags,
        websocket_paths=websocket_paths,
    )
