"""Projection and identifier mapping models."""

from __future__ import annotations

import uuid

from sqlalchemy import Float, ForeignKey, Integer, PrimaryKeyConstraint, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class IdMap(Base):
    """Canonical mapping between Yahoo and ESPN player identifiers."""

    __tablename__ = "id_map"
    __table_args__ = (UniqueConstraint("yahoo_player_id", name="uq_id_map_yahoo"),)

    canonical_player_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    yahoo_player_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    espn_player_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)


class WeeklyProjection(Base):
    """Projected fantasy points for a canonical player by week."""

    __tablename__ = "projections_weekly"
    __table_args__ = (
        PrimaryKeyConstraint("season", "week", "canonical_player_id", name="pk_projections_weekly"),
    )

    season: Mapped[int] = mapped_column(Integer, nullable=False)
    week: Mapped[int] = mapped_column(Integer, nullable=False)
    canonical_player_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("id_map.canonical_player_id", ondelete="CASCADE"),
        nullable=False,
    )
    points: Mapped[float] = mapped_column(Float, nullable=False)
