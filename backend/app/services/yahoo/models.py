"""Domain models describing Yahoo API ingestion payloads."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class YahooPlayerData:
    """Minimal projection of a Yahoo player record."""

    yahoo_player_id: str
    full_name: str
    position: str
    team_abbr: str | None
    status: str | None
    bye_week: int | None
    projected_points: float | None
    actual_points: float | None


@dataclass(slots=True)
class YahooRosterEntry:
    """Representation of a roster slot."""

    week: int
    slot: str
    player: YahooPlayerData
    is_starter: bool


@dataclass(slots=True)
class YahooTeamData:
    """Team-level metadata and roster payload."""

    team_key: str
    name: str
    manager: str
    is_user_team: bool
    roster: list[YahooRosterEntry] = field(default_factory=list)


@dataclass(slots=True)
class YahooLeagueData:
    """League metadata with nested teams."""

    league_key: str
    season: int
    name: str
    scoring_type: str
    status: str
    scoring_json: dict[str, Any]
    last_synced: datetime
    teams: list[YahooTeamData] = field(default_factory=list)


@dataclass(slots=True)
class YahooUserBundle:
    """Aggregate payload describing the authenticated user's fantasy context."""

    yahoo_sub: str
    yahoo_guid: str
    profile_nickname: str | None
    leagues: list[YahooLeagueData]
