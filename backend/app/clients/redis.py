"""Redis client scaffolding for caching and pub/sub."""

from dataclasses import dataclass

import redis.asyncio as redis

from app.core.config import Settings


@dataclass
class RedisClientFactory:
    """Produce Redis clients using Upstash connection strings."""

    settings: Settings

    def create(self) -> redis.Redis:  # pragma: no cover - placeholder
        """Instantiate an async Redis client configured for Upstash."""
        if not self.settings.redis_url:
            raise ValueError("REDIS_URL is not configured.")
        return redis.from_url(self.settings.redis_url, decode_responses=True)
