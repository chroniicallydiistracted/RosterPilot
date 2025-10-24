"""Game-centric endpoints backed by PyESPN fixtures (stubbed)."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import Settings
from app.dependencies.settings import provide_settings
from app.schemas.games import LiveGamesResponse, PlayByPlayResponse
from app.services.games import get_live_games_stub, get_play_by_play_stub

router = APIRouter(prefix="/games", tags=["games"])

SettingsDep = Annotated[Settings, Depends(provide_settings)]


@router.get("/live", summary="List currently live NFL games", response_model=LiveGamesResponse)
async def list_live_games(settings: SettingsDep) -> LiveGamesResponse:
    """Return a sample set of live games sourced from PyESPN fixtures."""

    _ = settings
    return get_live_games_stub()


@router.get(
    "/{event_id}/pbp",
    summary="Retrieve normalized play-by-play for an event",
    response_model=PlayByPlayResponse,
)
async def get_play_by_play(
    event_id: str,
    settings: SettingsDep,
) -> PlayByPlayResponse:
    """Return a stubbed play-by-play payload suitable for contract testing."""

    _ = settings
    return get_play_by_play_stub(event_id=event_id)
