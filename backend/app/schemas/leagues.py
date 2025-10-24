"""Schemas describing Yahoo league and roster responses."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class TeamSummary(BaseModel):
    """Metadata describing a Yahoo fantasy team."""

    team_key: str = Field(..., examples=["nfl.l.12345.t.1"])
    name: str = Field(..., examples=["Phoenix Firebirds"])
    manager: str = Field(..., examples=["Taylor Jenkins"])


class LeagueSummary(BaseModel):
    """High-level information about a Yahoo fantasy league."""

    league_key: str = Field(..., examples=["nfl.l.12345"])
    season: int = Field(..., ge=2000, le=2100, examples=[2024])
    name: str
    scoring_type: str = Field(..., description="Yahoo scoring designation")
    status: str = Field(..., description="League status such as pre_draft, in_season")
    my_team: TeamSummary
    source: Literal["yahoo"] = "yahoo"
    last_synced: datetime


class UserLeaguesResponse(BaseModel):
    """Response payload for `/me/leagues`."""

    generated_at: datetime
    leagues: list[LeagueSummary]


class PlayerProjection(BaseModel):
    """Projected performance for a rostered player."""

    yahoo_player_id: str
    full_name: str
    team_abbr: str
    position: str
    status: str | None = None
    projected_points: float
    actual_points: float | None = None


class RosterSlot(BaseModel):
    """Representation of a lineup slot and the recommended player."""

    slot: str
    player: PlayerProjection
    recommended: bool = Field(default=False)
    locked: bool = Field(default=False)


class OptimizerInsight(BaseModel):
    """Optimizer recommendation summary."""

    recommended_starters: list[str]
    delta_points: float
    rationale: list[str]
    source: Literal["optimizer"] = "optimizer"


class LeagueRosterResponse(BaseModel):
    """Response payload for `/leagues/{league_key}/roster`."""

    league_key: str
    week: int = Field(..., ge=1, le=18)
    team: TeamSummary
    generated_at: datetime
    starters: list[RosterSlot]
    bench: list[RosterSlot]
    optimizer: OptimizerInsight
