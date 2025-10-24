"""Game-centric endpoints backed by persisted PyESPN data."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.database import provide_db_session
from app.schemas.games import LiveGamesResponse, PlayByPlayResponse
from app.services.games import get_play_by_play, list_live_games

router = APIRouter(prefix="/games", tags=["games"])

SessionDep = Annotated[Session, Depends(provide_db_session)]


@router.get("/live", summary="List currently live NFL games", response_model=LiveGamesResponse)
async def list_live_games_route(session: SessionDep) -> LiveGamesResponse:
    """Return live game snapshots sourced from PyESPN ingestion."""

    return list_live_games(session)


@router.get(
    "/{event_id}/pbp",
    summary="Retrieve normalized play-by-play for an event",
    response_model=PlayByPlayResponse,
)
async def get_play_by_play_route(
    event_id: str,
    session: SessionDep,
) -> PlayByPlayResponse:
    """Return normalized play-by-play data for an event."""

    return get_play_by_play(session, event_id=event_id)
