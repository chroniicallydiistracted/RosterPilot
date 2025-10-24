"""Shared pytest fixtures for backend tests."""

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

os.environ["APP_ENV"] = "test"
os.environ["SENTRY_DSN"] = ""

from app.main import create_app  # noqa: E402


@pytest.fixture(scope="session")
def client() -> Iterator[TestClient]:
    """Provide a FastAPI test client backed by the scaffold application."""

    app = create_app()
    with TestClient(app) as test_client:
        yield test_client
