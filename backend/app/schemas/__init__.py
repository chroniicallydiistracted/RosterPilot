"""Pydantic schemas aggregated for convenient imports."""

from app.schemas.games import (
    DriveSummary,
    LiveGamesResponse,
    LiveGameSummary,
    PlayByPlayResponse,
    PlayDetail,
    TeamGameState,
    VenueInfo,
)
from app.schemas.health import HealthStatus
from app.schemas.leagues import (
    LeagueRosterResponse,
    LeagueSummary,
    OptimizerInsight,
    PlayerProjection,
    RosterSlot,
    TeamSummary,
    UserLeaguesResponse,
)
from app.schemas.runtime import FeatureFlags, RuntimeConfigResponse

__all__ = [
    "DriveSummary",
    "HealthStatus",
    "FeatureFlags",
    "LeagueRosterResponse",
    "LeagueSummary",
    "LiveGameSummary",
    "LiveGamesResponse",
    "OptimizerInsight",
    "PlayByPlayResponse",
    "PlayDetail",
    "PlayerProjection",
    "RuntimeConfigResponse",
    "RosterSlot",
    "TeamGameState",
    "TeamSummary",
    "UserLeaguesResponse",
    "VenueInfo",
]
