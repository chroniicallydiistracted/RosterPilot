"""Endpoints scoped to the authenticated Yahoo user."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.dependencies import provide_db_session
from app.dependencies.auth import provide_auth_context
from app.dependencies.settings import provide_settings
from app.schemas.leagues import UserLeaguesResponse
from app.services.leagues import list_user_leagues as list_user_leagues_service
from app.services.models import AuthContext

router = APIRouter(prefix="/me", tags=["me"])

SettingsDep = Annotated[Settings, Depends(provide_settings)]
AuthContextDep = Annotated[AuthContext, Depends(provide_auth_context)]
SessionDep = Annotated[Session, Depends(provide_db_session)]


@router.get(
    "/leagues",
    summary="List Yahoo leagues for the authenticated user",
    response_model=UserLeaguesResponse,
)
async def list_user_leagues(
    settings: SettingsDep,
    auth: AuthContextDep,
    session: SessionDep,
) -> UserLeaguesResponse:
    """Return the leagues discovered for the current Yahoo identity."""

    _ = settings
    return list_user_leagues_service(session=session, auth=auth)
