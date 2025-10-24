"""Database session dependency wiring."""

from __future__ import annotations

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.session import get_db_session
from app.dependencies.settings import provide_settings


def provide_db_session(
    settings: Annotated[Settings, Depends(provide_settings)]
) -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session tied to the current request lifecycle."""

    yield from get_db_session(settings)
