"""Schemas describing PyESPN game and play-by-play payloads."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class VenueInfo(BaseModel):
    """Simplified venue metadata."""

    venue_id: str
    name: str
    city: str
    state: str


class TeamGameState(BaseModel):
    """Scoreboard state for a team within an event."""

    espn_team_id: int
    name: str
    abbr: str
    score: int
    timeouts: int | None = Field(default=None, ge=0, le=3)


class LiveGameSummary(BaseModel):
    """High-level summary for a live or upcoming NFL game."""

    event_id: str
    season: int
    week: int
    status: str
    quarter: int | None = Field(default=None, ge=1, le=5)
    clock: str | None = None
    possession: str | None = None
    venue: VenueInfo
    home: TeamGameState
    away: TeamGameState
    last_update: datetime
    broadcast: dict[str, object]
    source: Literal["pyespn"] = "pyespn"


class LiveGamesResponse(BaseModel):
    """Response payload for `/games/live`."""

    generated_at: datetime
    games: list[LiveGameSummary]


class PlayDetail(BaseModel):
    """Normalized representation of a single play."""

    play_id: str
    sequence: int
    clock: str
    quarter: int
    down: int | None = Field(default=None, ge=1, le=4)
    distance: int | None = Field(default=None, ge=1)
    yardline_100: int | None = Field(default=None, ge=0, le=100)
    type: str = Field(alias="type", serialization_alias="type")  # noqa: A003
    yards: int | None = None
    description: str
    flags: list[str] = Field(default_factory=list)


class DriveSummary(BaseModel):
    """Sequence of plays comprising a drive."""

    drive_id: str
    team: TeamGameState
    result: str
    start_clock: str
    end_clock: str
    plays: list[PlayDetail]


class PlayByPlayResponse(BaseModel):
    """Response payload for `/games/{event_id}/pbp`."""

    event_id: str
    generated_at: datetime
    drives: list[DriveSummary]
    source: Literal["pyespn"] = "pyespn"
