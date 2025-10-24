"""League-centric API routes backed by Yahoo ingestion."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.dependencies import provide_db_session
from app.dependencies.auth import provide_auth_context
from app.dependencies.settings import provide_settings
from app.schemas.leagues import LeagueRosterResponse
from app.services.leagues import get_league_roster as get_league_roster_service
from app.services.models import AuthContext

router = APIRouter(prefix="/leagues", tags=["leagues"])

SettingsDep = Annotated[Settings, Depends(provide_settings)]
AuthContextDep = Annotated[AuthContext, Depends(provide_auth_context)]
SessionDep = Annotated[Session, Depends(provide_db_session)]


@router.get(
    "/{league_key}/roster",
    summary="Retrieve roster, projections, and optimizer insights for a league",
    response_model=LeagueRosterResponse,
)
async def get_league_roster(
    league_key: str,
    settings: SettingsDep,
    auth: AuthContextDep,
    session: SessionDep,
    week: int = Query(..., ge=1, le=18, description="Yahoo scoring week"),
) -> LeagueRosterResponse:
    """Return the user's roster for the requested week."""

    _ = settings
    try:
        return get_league_roster_service(session=session, auth=auth, league_key=league_key, week=week)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
