"""Authentication and authorization related dependency providers."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.dependencies.database import provide_db_session
from app.dependencies.settings import provide_settings
from app.models.user import User
from app.services.models import AuthContext

SettingsDep = Annotated[Settings, Depends(provide_settings)]
SessionDep = Annotated[Session, Depends(provide_db_session)]


def provide_auth_context(settings: SettingsDep, session: SessionDep) -> AuthContext:
    """Resolve the active Yahoo auth context for the current request."""

    _ = settings
    user = session.execute(select(User).order_by(User.created_at)).scalars().first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yahoo account has not been connected",
        )
    return AuthContext(user_id=user.user_id, yahoo_sub=user.yahoo_sub, scopes=["fspt-r"])
