"""HTTP client wrapper for retrieving PyESPN scoreboard and play data."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, cast

import httpx

from app.core.config import Settings

SCOREBOARD_ENDPOINT = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
PLAY_BY_PLAY_ENDPOINT = "https://cdn.espn.com/core/nfl/playbyplay"


@dataclass(slots=True)
class PyESPNClient:
    """Synchronous HTTP client for interacting with ESPN public APIs."""

    settings: Settings
    http_client: httpx.Client | None = None
    timeout: float = 10.0
    _client: httpx.Client = field(init=False, repr=False)
    _owns_client: bool = field(init=False, repr=False, default=False)

    def __post_init__(self) -> None:
        if self.http_client is not None:
            self._client = self.http_client
            self._owns_client = False
        else:
            self._client = httpx.Client(timeout=self.timeout)
            self._owns_client = True

    def close(self) -> None:
        """Release the underlying HTTP resources when owned by the client."""

        if self._owns_client:
            self._client.close()

    def get_scoreboard(
        self,
        season: int,
        week: int | None = None,
        *,
        extra_params: Mapping[str, str | int | float | bool | None] | None = None,
    ) -> dict[str, Any]:
        """Fetch the NFL scoreboard payload for a season/week window."""

        params: dict[str, str | int | float | bool | None] = {"limit": 50}
        if week is not None:
            params["week"] = week
            params["year"] = season
        else:
            params["dates"] = str(season)
        if extra_params:
            params.update(extra_params)

        response = self._client.get(SCOREBOARD_ENDPOINT, params=params)
        response.raise_for_status()
        return cast(dict[str, Any], response.json())

    def get_play_by_play(self, event_id: str) -> dict[str, Any]:
        """Fetch the detailed play-by-play timeline for a single event."""

        params: dict[str, str | int | float | bool | None] = {
            "gameId": event_id,
            "xhr": 1,
            "render": "false",
        }
        response = self._client.get(PLAY_BY_PLAY_ENDPOINT, params=params)
        response.raise_for_status()
        payload = cast(dict[str, Any], response.json())
        gamepackage = payload.get("gamepackageJSON")
        return cast(dict[str, Any], gamepackage) if isinstance(gamepackage, dict) else {}

    # FastAPI lifespan hooks expect async close support when using dependencies.
    async def aclose(self) -> None:  # pragma: no cover - sync close path used in tests
        self.close()
