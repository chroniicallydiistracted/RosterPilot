"""Integration tests covering security hardening behaviors."""

from __future__ import annotations

from http import HTTPStatus

from app.core.rate_limiter import SlidingWindowRateLimiter
from app.dependencies.rate_limit import provide_rate_limiter
from fastapi import Request
from fastapi.testclient import TestClient

P95_BUDGET_MS = 250.0


def test_oauth_rate_limit_enforced(client: TestClient) -> None:
    limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=60)

    async def _override_rate_limiter(request: Request) -> SlidingWindowRateLimiter:
        return limiter

    client.app.dependency_overrides[provide_rate_limiter] = _override_rate_limiter
    try:
        # Exhaust the small test allowance
        first = client.get("/api/auth/yahoo/authorize")
        assert first.status_code == HTTPStatus.OK
        second = client.get("/api/auth/yahoo/authorize")
        assert second.status_code == HTTPStatus.OK
        third = client.get("/api/auth/yahoo/authorize")
        assert third.status_code == HTTPStatus.TOO_MANY_REQUESTS
        assert third.headers.get("Retry-After") is not None
    finally:
        client.app.dependency_overrides.pop(provide_rate_limiter, None)


def test_request_metrics_header_and_budget(client: TestClient) -> None:
    client.app.state.request_metrics.reset()
    for _ in range(5):
        response = client.get("/api/games/live")
        assert response.status_code == HTTPStatus.OK
        assert "X-Request-Duration-Ms" in response.headers

    metrics = client.app.state.request_metrics
    p95 = metrics.percentile("/api/games/live", 0.95)
    assert p95 < P95_BUDGET_MS, f"Expected p95 under {P95_BUDGET_MS}ms, observed {p95}"
