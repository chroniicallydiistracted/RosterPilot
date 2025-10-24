"""WebSocket streaming for PyESPN-backed game deltas."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, status
from fastapi.websockets import WebSocketState
from pydantic import ValidationError
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.dependencies.database import provide_db_session
from app.dependencies.redis import provide_redis_client
from app.dependencies.settings import provide_settings
from app.models.espn import Play
from app.schemas.runtime import FeatureFlags
from app.schemas.ws import (
    ErrorMessage,
    GameDelta,
    GameDeltaEnvelope,
    HeartbeatMessage,
    ReplayCompleteMessage,
    WebSocketHandshake,
)
from app.services.games import build_play_detail

logger = logging.getLogger(__name__)

router = APIRouter()

MODE_LIVE = "live"
MODE_REPLAY = "replay"

SettingsDep = Annotated[Settings, Depends(provide_settings)]
RedisDep = Annotated[Redis, Depends(provide_redis_client)]
SessionDep = Annotated[Session, Depends(provide_db_session)]


@router.websocket("/games/{event_id}")
async def stream_game_updates(
    websocket: WebSocket,
    event_id: str,
    settings: SettingsDep,
    redis_client: RedisDep,
    session: SessionDep,
    mode: str = Query(default=MODE_LIVE, pattern=f"^({MODE_LIVE}|{MODE_REPLAY})$"),
    speed: float = Query(default=1.0, ge=0.0, le=8.0),
) -> None:
    """Stream live or replay play deltas to connected clients."""

    await websocket.accept()

    feature_flags = FeatureFlags(
        replay=settings.feature_replay,
        weather=settings.feature_weather,
    )
    handshake = WebSocketHandshake(
        event_id=event_id,
        mode=mode,
        heartbeat_sec=settings.ws_heartbeat_sec,
        feature_flags=feature_flags,
    )
    await _send_frame(websocket, handshake.model_dump(mode="json"))

    try:
        if mode == MODE_REPLAY:
            if not settings.feature_replay:
                await _send_frame(
                    websocket,
                    ErrorMessage(
                        event_id=event_id,
                        code="replay_disabled",
                        message="Replay streaming is disabled by configuration.",
                    ).model_dump(mode="json"),
                )
                await _close_socket(websocket, status.WS_1011_INTERNAL_ERROR)
                return
            await _stream_replay(
                websocket=websocket,
                session=session,
                event_id=event_id,
                speed=speed,
            )
            return

        await _stream_live(
            websocket=websocket,
            redis_client=redis_client,
            event_id=event_id,
            heartbeat_sec=settings.ws_heartbeat_sec,
        )
    except WebSocketDisconnect:
        logger.info("WebSocket disconnect for event %s", event_id)
    except Exception:  # pragma: no cover - defensive guard
        logger.exception("Unexpected error on websocket for event %s", event_id)
        await _send_frame(
            websocket,
            ErrorMessage(
                event_id=event_id,
                code="internal_error",
                message="An unexpected error occurred.",
            ).model_dump(mode="json"),
        )
        await _close_socket(websocket, status.WS_1011_INTERNAL_ERROR)


async def _stream_live(
    *,
    websocket: WebSocket,
    redis_client: Redis,
    event_id: str,
    heartbeat_sec: int,
) -> None:
    channel = f"game-deltas:{event_id}"
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel)

    try:
        while True:
            message = await pubsub.get_message(
                ignore_subscribe_messages=True,
                timeout=heartbeat_sec,
            )
            if message is None:
                await _send_frame(
                    websocket,
                    HeartbeatMessage(event_id=event_id).model_dump(mode="json"),
                )
                continue

            raw_data = message.get("data") if isinstance(message, dict) else None
            if raw_data is None:
                continue
            if isinstance(raw_data, bytes):
                raw_data = raw_data.decode("utf-8")

            try:
                payload = json.loads(raw_data)
            except (TypeError, json.JSONDecodeError):
                logger.warning("Discarding malformed delta for event %s", event_id)
                continue

            payload.setdefault("event_id", event_id)
            try:
                delta = GameDelta.model_validate(payload)
            except ValidationError as exc:
                logger.warning("Invalid delta payload for event %s: %s", event_id, exc)
                continue

            envelope = GameDeltaEnvelope(event_id=event_id, data=delta)
            await _send_frame(websocket, envelope.model_dump(mode="json"))
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()


async def _stream_replay(
    *,
    websocket: WebSocket,
    session: Session,
    event_id: str,
    speed: float,
) -> None:
    plays = list(
        session.execute(
            select(Play).where(Play.event_id == event_id).order_by(Play.drive_id, Play.sequence)
        ).scalars()
    )

    if not plays:
        await _send_frame(
            websocket,
            ErrorMessage(
                event_id=event_id,
                code="replay_unavailable",
                message="Replay data is not available for this event.",
            ).model_dump(mode="json"),
        )
        await _close_socket(websocket, status.WS_1008_POLICY_VIOLATION)
        return

    for play in plays:
        detail = build_play_detail(play)
        delta = GameDelta(
            event_id=event_id,
            play_id=play.play_id,
            sequence=detail.sequence,
            clock=detail.clock,
            quarter=detail.quarter,
            down=detail.down,
            distance=detail.distance,
            yardline_100=detail.yardline_100,
            type=detail.type,
            yards=detail.yards,
            flags=detail.flags,
            description=detail.description,
            replay=True,
            generated_at=datetime.now(tz=UTC),
        )
        await _send_frame(
            websocket,
            GameDeltaEnvelope(event_id=event_id, data=delta).model_dump(mode="json"),
        )
        if speed > 0:
            await asyncio.sleep(max(0.01, 1.0 / speed))

    await _send_frame(
        websocket, ReplayCompleteMessage(event_id=event_id).model_dump(mode="json")
    )


async def _send_frame(websocket: WebSocket, payload: dict[str, object]) -> None:
    if websocket.application_state == WebSocketState.DISCONNECTED:
        return
    await websocket.send_json(payload)


async def _close_socket(websocket: WebSocket, code: int) -> None:
    if websocket.application_state != WebSocketState.DISCONNECTED:
        await websocket.close(code=code)
