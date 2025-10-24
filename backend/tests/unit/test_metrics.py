"""Unit tests for the request metrics collector."""

from __future__ import annotations

import pytest
from app.core.metrics import RequestMetrics

TEST_ROUTE = "/api/demo"
SAMPLE_VALUES = [80.0, 120.0, 200.0, 40.0, 150.0]
FASTEST_SAMPLE_MS = min(SAMPLE_VALUES)
SLOWEST_SAMPLE_MS = max(SAMPLE_VALUES)
EMPTY_PERCENTILE_VALUE = 0.0


def test_records_and_reports_percentiles() -> None:
    metrics = RequestMetrics(max_samples=5)
    for value in SAMPLE_VALUES:
        metrics.record(TEST_ROUTE, value)

    assert metrics.percentile(TEST_ROUTE, 0.0) >= FASTEST_SAMPLE_MS
    assert metrics.percentile(TEST_ROUTE, 0.95) <= SLOWEST_SAMPLE_MS
    assert metrics.percentile(TEST_ROUTE, 1.0) == SLOWEST_SAMPLE_MS


def test_percentile_requires_valid_quantile() -> None:
    metrics = RequestMetrics()
    with pytest.raises(ValueError):
        metrics.percentile(TEST_ROUTE, -0.1)
    with pytest.raises(ValueError):
        metrics.percentile(TEST_ROUTE, 1.1)


def test_reset_clears_samples() -> None:
    metrics = RequestMetrics()
    metrics.record(TEST_ROUTE, 10.0)
    metrics.reset()
    assert metrics.percentile(TEST_ROUTE, 0.95) == EMPTY_PERCENTILE_VALUE
