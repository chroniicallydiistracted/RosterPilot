"""FastAPI dependencies for request rate limiting."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from app.core.config import Settings
from app.core.rate_limiter import RateLimitStatus, SlidingWindowRateLimiter
from app.dependencies.settings import provide_settings

SettingsDep = Annotated[Settings, Depends(provide_settings)]


async def provide_rate_limiter(request: Request, settings: SettingsDep) -> SlidingWindowRateLimiter:
    """Return (and lazily initialize) the process-wide rate limiter."""

    limiter: SlidingWindowRateLimiter | None = getattr(request.app.state, "rate_limiter", None)
    if (
        limiter is None
        or limiter.max_requests != settings.rate_limit_max
        or limiter.window_seconds != settings.rate_limit_window
    ):
        limiter = SlidingWindowRateLimiter(
            max_requests=settings.rate_limit_max,
            window_seconds=settings.rate_limit_window,
        )
        request.app.state.rate_limiter = limiter
    return limiter


async def enforce_rate_limit(
    request: Request,
    limiter: Annotated[SlidingWindowRateLimiter, Depends(provide_rate_limiter)],
) -> None:
    """Guard endpoint access based on client IP + path."""

    client_host = request.client.host if request.client else "anonymous"
    key = f"{client_host}:{request.url.path}"
    status_result: RateLimitStatus = limiter.check(key)
    if not status_result.allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again soon.",
            headers={"Retry-After": str(status_result.retry_after)},
        )
