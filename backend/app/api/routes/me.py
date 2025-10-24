"""Endpoints scoped to the authenticated Yahoo user."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import Settings
from app.dependencies.auth import provide_auth_context
from app.dependencies.settings import provide_settings
from app.schemas.leagues import UserLeaguesResponse
from app.services.leagues import get_user_leagues_stub
from app.services.models import AuthContext

router = APIRouter(prefix="/me", tags=["me"])

SettingsDep = Annotated[Settings, Depends(provide_settings)]
AuthContextDep = Annotated[AuthContext, Depends(provide_auth_context)]


@router.get(
    "/leagues",
    summary="List Yahoo leagues for the authenticated user",
    response_model=UserLeaguesResponse,
)
async def list_user_leagues(
    settings: SettingsDep,
    auth: AuthContextDep,
) -> UserLeaguesResponse:
    """Return the leagues discovered for the current Yahoo identity."""

    # Settings and auth are accepted to demonstrate dependency wiring for later phases.
    # They are not yet used by the scaffold implementation.
    _ = (settings, auth)
    return get_user_leagues_stub()
