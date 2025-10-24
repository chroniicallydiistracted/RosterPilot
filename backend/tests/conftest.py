"""Shared pytest fixtures for backend tests."""

from __future__ import annotations

import asyncio
import base64
import json
import os
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

TEST_DB_PATH = Path(__file__).resolve().parent / "test_app.db"

os.environ["APP_ENV"] = "test"
os.environ["SENTRY_DSN"] = ""
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"
os.environ["TOKEN_ENC_KEY"] = base64.urlsafe_b64encode(b"fernet-key-for-tests-32-bytes!!!").decode()
os.environ["SESSION_SECRET"] = "test-session-secret"
os.environ["YAHOO_CLIENT_ID"] = "test-client-id"
os.environ["YAHOO_CLIENT_SECRET"] = "test-client-secret"
os.environ["YAHOO_REDIRECT_URI"] = "https://example.com/callback"
os.environ["PYESPN_SEASON_YEAR"] = "2022"
os.environ["WS_HEARTBEAT_SEC"] = "1"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.dependencies import provide_db_session, provide_redis_client
from app.db.session import _engine
from app.jobs.reference import seed_canonical_players, seed_reference_data
from app.main import create_app  # noqa: E402
from app.models import Base
from app.security.crypto import TokenCipher
from app.services.pyespn.ingest import PyESPNIngestionService
from app.services.yahoo.fixtures import load_test_user_bundle
from app.services.yahoo.ingest import YahooIngestionService
from .fixtures.pyespn import load_play_by_play_fixture, load_scoreboard_fixture


class FakeRedisPubSub:
    """Minimal async pub/sub stub for websocket tests."""

    def __init__(self) -> None:
        self._queue: asyncio.Queue[dict[str, object]] = asyncio.Queue()
        self._closed = False

    async def subscribe(self, _channel: str) -> None:  # pragma: no cover - trivial
        return

    async def unsubscribe(self, _channel: str) -> None:  # pragma: no cover - trivial
        return

    async def close(self) -> None:
        self._closed = True

    async def get_message(self, *, ignore_subscribe_messages: bool, timeout: float | None):
        if self._closed:
            return None
        try:
            if timeout is None or timeout <= 0:
                item = await asyncio.wait_for(self._queue.get(), timeout=0.05)
            else:
                item = await asyncio.wait_for(self._queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None
        if ignore_subscribe_messages:
            return item
        return item

    def push_json(self, payload: dict[str, object]) -> None:
        self._queue.put_nowait({"type": "message", "data": json.dumps(payload)})


class FakeRedis:
    """Redis client stub supporting pubsub()."""

    def __init__(self) -> None:
        self.pubsub_instance = FakeRedisPubSub()

    def pubsub(self) -> FakeRedisPubSub:
        return self.pubsub_instance

    async def close(self) -> None:  # pragma: no cover - trivial
        return

    async def wait_closed(self) -> None:  # pragma: no cover - trivial
        return


class FakeRedisProvider:
    """Dependency override that tracks the most recent Redis stub."""

    def __init__(self) -> None:
        self.instances: list[FakeRedis] = []

    async def dependency(self) -> AsyncIterator[FakeRedis]:
        client = FakeRedis()
        self.instances.append(client)
        try:
            yield client
        finally:  # pragma: no cover - cleanup placeholder
            await client.close()

get_settings.cache_clear()


@pytest.fixture(scope="session", autouse=True)
def _initialize_database() -> Iterator[None]:
    """Create the SQLite schema and seed Yahoo fixtures for tests."""

    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    get_settings.cache_clear()
    settings = get_settings()
    database_url = settings.database_url or f"sqlite:///{TEST_DB_PATH}"
    engine = _engine(database_url)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        seed_reference_data(session)
        seed_canonical_players(session)
        session.commit()

        cipher = TokenCipher.from_settings(settings)
        ingestion = YahooIngestionService(session=session, cipher=cipher)
        bundle = load_test_user_bundle()
        ingestion.ingest_bundle(bundle)

        pyespn_ingestion = PyESPNIngestionService(session=session)
        scoreboard = load_scoreboard_fixture()
        pyespn_ingestion.ingest_scoreboard(scoreboard)
        pyespn_ingestion.ingest_play_by_play(
            "401437933", load_play_by_play_fixture("401437933")
        )
        session.commit()

    yield


@pytest.fixture(scope="session")
def client() -> Iterator[TestClient]:
    """Provide a FastAPI test client backed by the scaffold application."""

    get_settings.cache_clear()
    settings = get_settings()
    database_url = settings.database_url or f"sqlite:///{TEST_DB_PATH}"
    app = create_app()

    session_factory = sessionmaker(bind=_engine(database_url), autoflush=False, autocommit=False, expire_on_commit=False)

    def override_db_session():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[provide_db_session] = override_db_session
    fake_redis_provider = FakeRedisProvider()

    async def override_redis_client():
        async for client in fake_redis_provider.dependency():
            yield client

    app.dependency_overrides[provide_redis_client] = override_redis_client
    app.state.fake_redis_provider = fake_redis_provider
    with TestClient(app) as test_client:
        yield test_client
