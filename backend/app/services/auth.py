"""Authentication and OAuth orchestration services."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, cast
from urllib.parse import urlencode

import httpx
from sqlalchemy.orm import Session

from app.clients.yahoo import YahooClient
from app.core.config import Settings
from app.security.crypto import TokenCipher
from app.security.state import OAuthStateManager
from app.services.yahoo.ingest import TokenPayload, YahooIngestionService
from app.services.yahoo.models import YahooUserBundle


@dataclass(slots=True)
class OAuthExchangeResult:
    """Outcome returned after successfully handling an OAuth callback."""

    user_id: str
    yahoo_sub: str
    expires_at: datetime


class YahooOAuthService:
    """Handle Yahoo OAuth authorization flows."""

    def __init__(self, settings: Settings, http_client: httpx.AsyncClient | None = None) -> None:
        self.settings = settings
        self._http_client = http_client or httpx.AsyncClient(timeout=httpx.Timeout(15.0, read=30.0))

    def build_authorization_url(self, state: str) -> str:
        """Construct the Yahoo OAuth authorization URL."""

        params = {
            "client_id": self.settings.yahoo_client_id,
            "redirect_uri": self.settings.yahoo_redirect_uri,
            "response_type": "code",
            "scope": self.settings.yahoo_scope,
            "state": state,
        }
        if not all(params.values()):
            raise ValueError("Yahoo OAuth configuration is incomplete")
        return f"https://api.login.yahoo.com/oauth2/request_auth?{urlencode(params)}"

    async def exchange_code(self, code: str) -> dict[str, Any]:
        """Exchange the authorization code for Yahoo tokens."""

        token_endpoint = YahooClient.TOKEN_ENDPOINT_URL
        auth = (self.settings.yahoo_client_id or "", self.settings.yahoo_client_secret or "")
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.settings.yahoo_redirect_uri,
        }
        response = await self._http_client.post(token_endpoint, auth=auth, data=payload)
        response.raise_for_status()
        return cast(dict[str, Any], response.json())

    async def fetch_user_info(self, access_token: str) -> dict[str, Any]:
        """Retrieve OpenID profile information for the authenticated Yahoo user."""

        headers = {"Authorization": f"Bearer {access_token}"}
        response = await self._http_client.get(YahooClient.USER_INFO_ENDPOINT, headers=headers)
        response.raise_for_status()
        return cast(dict[str, Any], response.json())

    async def handle_callback(
        self,
        code: str,
        state: str,
        session: Session,
    ) -> OAuthExchangeResult:
        """Process the OAuth callback and trigger ingestion."""

        OAuthStateManager(settings=self.settings).verify(state)
        token_payload = await self.exchange_code(code)

        access_token = token_payload["access_token"]
        refresh_token = token_payload.get("refresh_token", "")
        expires_in = int(token_payload.get("expires_in", 3600))
        scopes = token_payload.get("scope", self.settings.yahoo_scope)
        expires_at = datetime.now(tz=UTC) + timedelta(seconds=expires_in)

        user_info = await self.fetch_user_info(access_token)
        yahoo_sub = user_info.get("sub") or user_info.get("user_id")
        if not yahoo_sub:
            raise RuntimeError("Yahoo user info did not include a subject identifier")

        bundle = await self._load_user_bundle(access_token)
        bundle.yahoo_sub = yahoo_sub  # ensure DB user key matches OpenID subject

        cipher = TokenCipher.from_settings(self.settings)
        ingestion = YahooIngestionService(session=session, cipher=cipher)
        user = ingestion.ingest_bundle(bundle)
        ingestion.store_tokens(
            user=user,
            payload=TokenPayload(
                provider="yahoo",
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at,
                scopes=scopes,
            ),
        )

        session.commit()
        return OAuthExchangeResult(
            user_id=str(user.user_id),
            yahoo_sub=yahoo_sub,
            expires_at=expires_at,
        )

    async def _load_user_bundle(self, access_token: str) -> YahooUserBundle:
        """Retrieve the Yahoo user bundle using the provided access token."""

        client = YahooClient(settings=self.settings, access_token=access_token)
        return await client.fetch_user_bundle()

    async def aclose(self) -> None:  # pragma: no cover - context helper
        await self._http_client.aclose()
