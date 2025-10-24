"""Yahoo Fantasy Sports API client abstraction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

import httpx

from app.core.config import Settings
from app.services.yahoo.fixtures import load_test_user_bundle
from app.services.yahoo.models import YahooUserBundle


@dataclass(slots=True)
class YahooClient:
    """Client responsible for communicating with the Yahoo Fantasy APIs."""

    settings: Settings
    access_token: str | None = None
    http_client: httpx.AsyncClient | None = None

    BASE_URL: ClassVar[str] = "https://fantasysports.yahooapis.com/fantasy/v2"
    TOKEN_ENDPOINT: ClassVar[str] = "https://api.login.yahoo.com/oauth2/get_token"
    USER_INFO_ENDPOINT: ClassVar[str] = "https://api.login.yahoo.com/openid/v1/userinfo"

    async def fetch_user_bundle(self) -> YahooUserBundle:
        """Return the authenticated user's fantasy context."""

        if self.settings.environment == "test":
            # Test and scaffold environments leverage deterministic fixtures to
            # avoid live Yahoo calls while validating downstream persistence.
            return load_test_user_bundle()

        # The live implementation will hydrate `YahooUserBundle` by composing
        # Yahoo Fantasy API responses. This placeholder guards future work.
        raise NotImplementedError("Live Yahoo API integration is pending implementation.")

    async def __aenter__(self) -> "YahooClient":  # pragma: no cover - context helper
        if self.http_client is None:
            self.http_client = httpx.AsyncClient(timeout=httpx.Timeout(15.0, read=30.0))
        return self

    async def __aexit__(self, *exc_info: object) -> None:  # pragma: no cover - context helper
        if self.http_client is not None:
            await self.http_client.aclose()
            self.http_client = None
