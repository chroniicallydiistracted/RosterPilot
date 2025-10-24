"""Database engine and session management utilities."""

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings


class DatabaseNotConfiguredError(RuntimeError):
    """Raised when a database-dependent dependency is invoked without configuration."""


@lru_cache
def _engine(database_url: str) -> Engine:
    if not database_url:
        raise DatabaseNotConfiguredError("DATABASE_URL is not configured.")
    if database_url.startswith("sqlite"):
        return create_engine(
            database_url,
            pool_pre_ping=True,
            future=True,
            connect_args={"check_same_thread": False},
        )
    return create_engine(database_url, pool_pre_ping=True, future=True)


def get_session_factory(settings: Settings) -> sessionmaker[Session]:
    """Return a SQLAlchemy sessionmaker bound to the configured database."""
    database_url = settings.database_url or ""
    return sessionmaker(
        bind=_engine(database_url), autoflush=False, autocommit=False, expire_on_commit=False
    )


def get_db_session(settings: Settings) -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session."""
    factory = get_session_factory(settings)
    session = factory()
    try:
        yield session
    finally:  # pragma: no cover - control flow placeholder
        session.close()
