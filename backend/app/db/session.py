"""Database engine and session management utilities."""

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings


class DatabaseNotConfiguredError(RuntimeError):
    """Raised when a database-dependent dependency is invoked without configuration."""


@lru_cache
def _engine(settings: Settings) -> Engine:
    if not settings.database_url:
        raise DatabaseNotConfiguredError("DATABASE_URL is not configured.")
    return create_engine(settings.database_url, pool_pre_ping=True, future=True)


def get_session_factory(settings: Settings) -> sessionmaker[Session]:
    """Return a SQLAlchemy sessionmaker bound to the configured database."""
    return sessionmaker(
        bind=_engine(settings), autoflush=False, autocommit=False, expire_on_commit=False
    )


def get_db_session(settings: Settings) -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session."""
    factory = get_session_factory(settings)
    session = factory()
    try:
        yield session
    finally:  # pragma: no cover - control flow placeholder
        session.close()
