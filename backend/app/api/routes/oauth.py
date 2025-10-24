"""OAuth endpoints for Yahoo authentication."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.dependencies import enforce_rate_limit, provide_db_session
from app.dependencies.settings import provide_settings
from app.security.state import OAuthStateError, OAuthStateManager
from app.services.auth import YahooOAuthService

router = APIRouter(prefix="/auth", tags=["auth"])

SettingsDep = Annotated[Settings, Depends(provide_settings)]
SessionDep = Annotated[Session, Depends(provide_db_session)]


@router.get("/yahoo/authorize", dependencies=[Depends(enforce_rate_limit)])
async def yahoo_authorize(settings: SettingsDep) -> dict[str, str]:
    """Generate the Yahoo authorization URL and state token."""

    state_manager = OAuthStateManager(settings=settings)
    state = state_manager.issue()
    service = YahooOAuthService(settings=settings)
    try:
        url = service.build_authorization_url(state=state)
    finally:
        await service.aclose()
    return {"authorization_url": url, "state": state}


@router.get("/yahoo/callback", dependencies=[Depends(enforce_rate_limit)])
async def yahoo_callback(
    settings: SettingsDep,
    session: SessionDep,
    code: str = Query(..., description="Authorization code returned by Yahoo"),
    state: str = Query(..., description="Opaque OAuth state value"),
) -> dict[str, str]:
    """Handle the Yahoo OAuth callback and persist tokens."""

    try:
        service = YahooOAuthService(settings=settings)
        result = await service.handle_callback(code=code, state=state, session=session)
    except OAuthStateError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive catch for integration errors
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    finally:
        if "service" in locals():
            await service.aclose()

    return {
        "user_id": result.user_id,
        "yahoo_sub": result.yahoo_sub,
        "expires_at": result.expires_at.isoformat(),
    }
