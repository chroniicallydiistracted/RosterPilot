"""Authentication and authorization related dependency providers."""

from typing import Annotated

from fastapi import Depends

from app.core.config import Settings
from app.dependencies.settings import provide_settings
from app.services.models import AuthContext

SettingsDep = Annotated[Settings, Depends(provide_settings)]


def provide_auth_context(settings: SettingsDep) -> AuthContext:
    """Return a placeholder auth context used for contract testing."""

    # In later phases this will decode Yahoo OAuth tokens and hydrate the context.
    _ = settings
    return AuthContext(
        user_id="demo-user",
        yahoo_sub="demo-sub",
        scopes=["fspt-r"],
    )
