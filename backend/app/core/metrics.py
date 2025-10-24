"""Lightweight metrics collector for HTTP request timing."""

from __future__ import annotations

import bisect
from collections import defaultdict
from threading import Lock


class RequestMetrics:
    """Store bounded timing samples per route for percentile checks."""

    def __init__(self, max_samples: int = 512) -> None:
        if max_samples <= 0:
            raise ValueError("max_samples must be positive")
        self._max_samples = max_samples
        self._samples: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def record(self, route: str, duration_ms: float) -> None:
        """Add a timing sample for ``route``."""

        with self._lock:
            samples = self._samples[route]
            bisect.insort(samples, duration_ms)
            # Keep the largest samples (slowest requests) when trimming to the budget.
            if len(samples) > self._max_samples:
                del samples[0 : len(samples) - self._max_samples]

    def percentile(self, route: str, quantile: float) -> float:
        """Return the latency percentile for ``route`` (0-1 range)."""

        if not 0 <= quantile <= 1:
            raise ValueError("quantile must be between 0 and 1")

        with self._lock:
            samples = self._samples.get(route)
            if not samples:
                return 0.0
            if quantile == 1:
                return samples[-1]
            index = int((len(samples) - 1) * quantile)
            return samples[index]

    def reset(self) -> None:
        """Clear collected samples (useful for testing)."""

        with self._lock:
            self._samples.clear()
