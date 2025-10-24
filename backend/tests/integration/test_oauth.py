"""Integration tests covering the Yahoo OAuth flow."""

from __future__ import annotations

import uuid

import httpx
import respx
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import _engine
from app.models.user import OAuthToken, User


def test_authorize_endpoint_returns_state(client: TestClient) -> None:
    response = client.get("/api/auth/yahoo/authorize")
    assert response.status_code == 200
    data = response.json()
    assert "state" in data
    assert "authorization_url" in data
    assert "client_id=test-client-id" in data["authorization_url"]


@respx.mock
def test_callback_exchanges_code_and_persists_tokens(client: TestClient) -> None:
    authorize = client.get("/api/auth/yahoo/authorize")
    state = authorize.json()["state"]

    token_route = respx.post("https://api.login.yahoo.com/oauth2/get_token").mock(
        return_value=httpx.Response(
            200,
            json={
                "access_token": "access-token-xyz",
                "refresh_token": "refresh-token-xyz",
                "expires_in": 3600,
                "scope": "fspt-r",
            },
        )
    )
    userinfo_route = respx.get("https://api.login.yahoo.com/openid/v1/userinfo").mock(
        return_value=httpx.Response(200, json={"sub": "demo-sub-callback"})
    )

    response = client.get(
        "/api/auth/yahoo/callback",
        params={"code": "mock-code", "state": state},
    )
    assert response.status_code == 200
    data = response.json()

    assert token_route.called
    assert userinfo_route.called
    assert data["yahoo_sub"] == "demo-sub-callback"

    settings = get_settings()
    engine = _engine(settings.database_url or "")
    with Session(engine) as session:
        user = session.execute(select(User).where(User.yahoo_sub == "demo-sub-callback")).scalar_one()
        token = session.execute(
            select(OAuthToken).where(OAuthToken.user_id == user.user_id, OAuthToken.provider == "yahoo")
        ).scalar_one()

        assert uuid.UUID(data["user_id"]) == user.user_id
        assert token.access_token != "access-token-xyz"
        assert token.refresh_token != "refresh-token-xyz"
