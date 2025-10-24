"""Thread-safe sliding window rate limiter for request throttling."""

from __future__ import annotations

import math
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from threading import Lock


@dataclass(slots=True)
class RateLimitStatus:
    """Result from evaluating a rate limit decision."""

    allowed: bool
    remaining: int
    reset_at: float

    @property
    def retry_after(self) -> int:
        """Return the Retry-After value in seconds."""

        remaining = max(0.0, self.reset_at - time.time())
        return max(0, int(math.ceil(remaining)))


class SlidingWindowRateLimiter:
    """Maintain request counts within a moving window for many keys."""

    def __init__(self, max_requests: int, window_seconds: int) -> None:
        if max_requests <= 0:
            raise ValueError("max_requests must be positive")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")

        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str, *, now: float | None = None) -> RateLimitStatus:
        """Record a hit for ``key`` and determine if it is still allowed."""

        current_ts = now if now is not None else time.time()
        window_floor = current_ts - self.window_seconds

        with self._lock:
            queue = self._hits[key]
            while queue and queue[0] <= window_floor:
                queue.popleft()

            if len(queue) >= self.max_requests:
                reset_at = queue[0] + self.window_seconds if queue else current_ts
                return RateLimitStatus(allowed=False, remaining=0, reset_at=reset_at)

            queue.append(current_ts)
            remaining = max(0, self.max_requests - len(queue))
            return RateLimitStatus(
                allowed=True,
                remaining=remaining,
                reset_at=current_ts + self.window_seconds,
            )

    def reset(self) -> None:
        """Clear all stored request history."""

        with self._lock:
            self._hits.clear()
