"""League-centric API routes with stubbed responses."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.config import Settings
from app.dependencies.auth import provide_auth_context
from app.dependencies.settings import provide_settings
from app.schemas.leagues import LeagueRosterResponse
from app.services.leagues import get_league_roster_stub
from app.services.models import AuthContext

router = APIRouter(prefix="/leagues", tags=["leagues"])

SettingsDep = Annotated[Settings, Depends(provide_settings)]
AuthContextDep = Annotated[AuthContext, Depends(provide_auth_context)]


@router.get(
    "/{league_key}/roster",
    summary="Retrieve roster, projections, and optimizer insights for a league",
    response_model=LeagueRosterResponse,
)
async def get_league_roster(
    league_key: str,
    settings: SettingsDep,
    auth: AuthContextDep,
    week: int = Query(..., ge=1, le=18, description="Yahoo scoring week"),
) -> LeagueRosterResponse:
    """Return a stubbed roster payload suitable for contract testing."""

    _ = (settings, auth)
    return get_league_roster_stub(league_key=league_key, week=week)
