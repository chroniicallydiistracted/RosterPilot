"""Yahoo Fantasy Sports API client scaffolding."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import Settings


@dataclass
class YahooClient:
    """Minimal Yahoo API client placeholder.

    The implementation will handle OAuth flows, token refresh, and data ingestion in later phases.
    """

    settings: Settings
    http_client: httpx.AsyncClient | None = None

    BASE_URL: str = "https://fantasysports.yahooapis.com/fantasy/v2"

    async def get_leagues(self) -> Any:  # pragma: no cover - placeholder
        """Fetch leagues for the authenticated user (stub)."""
        raise NotImplementedError("Yahoo client integration not yet implemented.")
