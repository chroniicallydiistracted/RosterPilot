"""Data structures used by the lineup optimizer pipeline."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OptimizerPlayer:
    """Player candidate considered by the optimizer."""

    player_id: str
    name: str
    positions: tuple[str, ...]
    projected_points: float
    status: str | None = None


@dataclass(frozen=True, slots=True)
class OptimizerSlot:
    """Starting lineup slot to fill during optimization."""

    slot_id: str
    slot_name: str
    eligible_positions: tuple[str, ...]
    current_player_id: str | None = None


@dataclass(frozen=True, slots=True)
class OptimizerAssignment:
    """Mapping of a slot to the player selected for that role."""

    slot_id: str
    slot_name: str
    player_id: str
    projected_points: float


@dataclass(frozen=True, slots=True)
class OptimizerResult:
    """Outcome returned from the lineup optimizer."""

    assignments: tuple[OptimizerAssignment, ...]
    total_points: float
    fallback_used: bool = False

    @property
    def recommended_player_ids(self) -> set[str]:
        """Return the player identifiers selected for the starting lineup."""

        return {assignment.player_id for assignment in self.assignments}

