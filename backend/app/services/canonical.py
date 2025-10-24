"""Utilities for reconciling canonical player identifiers across providers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.espn import Athlete
from app.models.projection import IdMap


@dataclass(slots=True, frozen=True)
class CanonicalPlayerReference:
    """Manual or reference-driven player mapping metadata."""

    full_name: str
    position: str
    team_abbr: str | None
    yahoo_player_id: str | None
    espn_player_id: str | None
    confidence: float = 1.0
    is_manual: bool = True


class PlayerReconciliationService:
    """Apply canonical mapping references to the identifier map."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def reconcile(self, references: Iterable[CanonicalPlayerReference]) -> list[IdMap]:
        """Upsert `IdMap` rows according to the provided references."""

        reconciled: list[IdMap] = []
        for reference in references:
            id_map = self._locate_mapping(reference)
            if id_map is None:
                id_map = IdMap(
                    yahoo_player_id=reference.yahoo_player_id,
                    espn_player_id=reference.espn_player_id,
                    full_name=reference.full_name,
                    position=reference.position,
                    team_abbr=reference.team_abbr,
                    confidence=reference.confidence,
                    is_manual=reference.is_manual,
                )
                self.session.add(id_map)
            else:
                if reference.yahoo_player_id:
                    id_map.yahoo_player_id = reference.yahoo_player_id
                if reference.espn_player_id:
                    id_map.espn_player_id = reference.espn_player_id
                id_map.full_name = reference.full_name
                id_map.position = reference.position
                id_map.team_abbr = reference.team_abbr
                id_map.confidence = max(reference.confidence, id_map.confidence)
                id_map.is_manual = id_map.is_manual or reference.is_manual

            if reference.espn_player_id:
                self._upsert_athlete(reference)

            reconciled.append(id_map)

        return reconciled

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _locate_mapping(self, reference: CanonicalPlayerReference) -> IdMap | None:
        """Retrieve an existing mapping candidate for the reference."""

        if reference.yahoo_player_id:
            mapping = self.session.execute(
                select(IdMap).where(IdMap.yahoo_player_id == reference.yahoo_player_id)
            ).scalar_one_or_none()
            if mapping is not None:
                return mapping
        if reference.espn_player_id:
            return self.session.execute(
                select(IdMap).where(IdMap.espn_player_id == reference.espn_player_id)
            ).scalar_one_or_none()
        return None

    def _upsert_athlete(self, reference: CanonicalPlayerReference) -> Athlete:
        """Ensure the ESPN athlete table mirrors the reference data."""

        athlete = self.session.get(Athlete, reference.espn_player_id)
        if athlete is None:
            athlete = Athlete(
                espn_player_id=reference.espn_player_id,
                full_name=reference.full_name,
                position=reference.position,
                team_abbr=reference.team_abbr,
                active=True,
            )
            self.session.add(athlete)
        else:
            athlete.full_name = reference.full_name
            athlete.position = reference.position
            athlete.team_abbr = reference.team_abbr
            athlete.active = True
        return athlete


__all__: Sequence[str] = [
    "CanonicalPlayerReference",
    "PlayerReconciliationService",
]
