"""Unit coverage for the sliding window rate limiter."""

from __future__ import annotations

import pytest
from app.core.rate_limiter import SlidingWindowRateLimiter

DEFAULT_KEY = "client"
BUDGET_MAX_REQUESTS = 3
BUDGET_WINDOW_SECONDS = 10
SMALL_WINDOW_SECONDS = 1


def test_rate_limiter_allows_within_budget() -> None:
    limiter = SlidingWindowRateLimiter(
        max_requests=BUDGET_MAX_REQUESTS,
        window_seconds=BUDGET_WINDOW_SECONDS,
    )
    for _ in range(BUDGET_MAX_REQUESTS):
        result = limiter.check(DEFAULT_KEY)
        assert result.allowed
    denied = limiter.check(DEFAULT_KEY)
    assert not denied.allowed
    assert denied.remaining == 0
    assert denied.retry_after >= 0


def test_rate_limiter_resets_after_window() -> None:
    limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=SMALL_WINDOW_SECONDS)
    limiter.check(DEFAULT_KEY, now=0.0)
    limiter.check(DEFAULT_KEY, now=0.2)
    blocked = limiter.check(DEFAULT_KEY, now=0.5)
    assert not blocked.allowed
    # Advance past the oldest timestamp in the window
    allowed = limiter.check(DEFAULT_KEY, now=1.21)
    assert allowed.allowed


def test_invalid_configuration() -> None:
    with pytest.raises(ValueError):
        SlidingWindowRateLimiter(max_requests=0, window_seconds=1)
    with pytest.raises(ValueError):
        SlidingWindowRateLimiter(max_requests=1, window_seconds=0)
