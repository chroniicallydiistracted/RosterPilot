"""Helpers to load recorded PyESPN fixtures for tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

FIXTURE_DIR = Path(__file__).resolve().parent


def load_scoreboard_fixture() -> dict[str, Any]:
    """Load the recorded scoreboard payload bundled with the repo."""

    with (FIXTURE_DIR / "scoreboard_2023_01_01.json").open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_play_by_play_fixture(event_id: str) -> dict[str, Any]:
    """Load the play-by-play fixture for a specific event id."""

    path = FIXTURE_DIR / f"pbp_{event_id}.json"
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
