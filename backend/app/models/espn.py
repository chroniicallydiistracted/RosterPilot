"""Persistence models for PyESPN-derived data."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Team(Base):
    """NFL team metadata sourced from PyESPN."""

    __tablename__ = "teams"

    espn_team_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    abbr: Mapped[str] = mapped_column(String(8), nullable=False)
    colors_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    logos_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)


class Venue(Base):
    """NFL venue metadata."""

    __tablename__ = "venues"

    venue_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    city: Mapped[str] = mapped_column(String(128), nullable=False)
    roof_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    surface: Mapped[str | None] = mapped_column(String(32), nullable=True)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lon: Mapped[float | None] = mapped_column(Float, nullable=True)


class Event(Base):
    """NFL event (game) metadata."""

    __tablename__ = "events"

    event_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    season: Mapped[int] = mapped_column(Integer, nullable=False)
    week: Mapped[int] = mapped_column(Integer, nullable=False)
    start_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    home_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teams.espn_team_id", ondelete="RESTRICT"), nullable=False
    )
    away_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teams.espn_team_id", ondelete="RESTRICT"), nullable=False
    )
    venue_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("venues.venue_id", ondelete="SET NULL"), nullable=True
    )


class Drive(Base):
    """Drive metadata for play-by-play sequences."""

    __tablename__ = "drives"
    __table_args__ = (PrimaryKeyConstraint("event_id", "drive_id", name="pk_drives"),)

    event_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("events.event_id", ondelete="CASCADE"), nullable=False
    )
    drive_id: Mapped[str] = mapped_column(String(16), nullable=False)
    start_yardline_100: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_yardline_100: Mapped[int | None] = mapped_column(Integer, nullable=True)
    result: Mapped[str | None] = mapped_column(String(64), nullable=True)
    start_clock: Mapped[str | None] = mapped_column(String(16), nullable=True)
    end_clock: Mapped[str | None] = mapped_column(String(16), nullable=True)


class Play(Base):
    """Normalized play-by-play record."""

    __tablename__ = "plays"
    __table_args__ = (PrimaryKeyConstraint("event_id", "play_id", name="pk_plays"),)

    event_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("events.event_id", ondelete="CASCADE"), nullable=False
    )
    play_id: Mapped[str] = mapped_column(String(32), nullable=False)
    drive_id: Mapped[str] = mapped_column(String(16), nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    clock: Mapped[str | None] = mapped_column(String(16), nullable=True)
    quarter: Mapped[int | None] = mapped_column(Integer, nullable=True)
    down: Mapped[int | None] = mapped_column(Integer, nullable=True)
    distance: Mapped[int | None] = mapped_column(Integer, nullable=True)
    yardline_100: Mapped[int | None] = mapped_column(Integer, nullable=True)
    type: Mapped[str | None] = mapped_column(String(32), nullable=True)  # noqa: A003
    yards: Mapped[int | None] = mapped_column(Integer, nullable=True)
    raw_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
