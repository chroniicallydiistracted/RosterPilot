"""Persistence models for Yahoo fantasy data."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    String,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class YahooLeague(Base):
    """Yahoo fantasy league metadata."""

    __tablename__ = "yahoo_leagues"

    league_key: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    season: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    scoring_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="in_season")
    last_synced: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class YahooTeam(Base):
    """Team metadata within a Yahoo fantasy league."""

    __tablename__ = "yahoo_teams"

    team_key: Mapped[str] = mapped_column(String(64), primary_key=True)
    league_key: Mapped[str] = mapped_column(
        String(64), ForeignKey("yahoo_leagues.league_key", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    manager: Mapped[str] = mapped_column(String(128), nullable=False)
    is_user_team: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class YahooPlayer(Base):
    """Yahoo player metadata persisted for roster joins."""

    __tablename__ = "yahoo_players"

    yahoo_player_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    pos: Mapped[str] = mapped_column(String(16), nullable=False)
    team_abbr: Mapped[str | None] = mapped_column(String(8), nullable=True)
    status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    bye_week: Mapped[int | None] = mapped_column(Integer, nullable=True)


class YahooRoster(Base):
    """Roster slots with associated Yahoo player IDs."""

    __tablename__ = "yahoo_rosters"
    __table_args__ = (PrimaryKeyConstraint("team_key", "week", "slot", name="pk_yahoo_rosters"),)

    team_key: Mapped[str] = mapped_column(
        String(64), ForeignKey("yahoo_teams.team_key", ondelete="CASCADE"), nullable=False
    )
    week: Mapped[int] = mapped_column(Integer, nullable=False)
    slot: Mapped[str] = mapped_column(String(32), nullable=False)
    yahoo_player_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("yahoo_players.yahoo_player_id", ondelete="SET NULL"), nullable=True
    )
    is_starter: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    projected_points: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    actual_points: Mapped[float | None] = mapped_column(Float, nullable=True)
