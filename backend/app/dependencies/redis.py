"""Redis dependency wiring for realtime features."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from app.clients.redis import RedisClientFactory
from app.core.config import Settings
from app.dependencies.settings import provide_settings


async def provide_redis_client(
    settings: Annotated[Settings, Depends(provide_settings)]
) -> AsyncIterator[Redis]:
    """Yield an async Redis client configured via application settings."""

    factory = RedisClientFactory(settings=settings)
    client = factory.create()
    try:
        yield client
    finally:
        await client.aclose()
