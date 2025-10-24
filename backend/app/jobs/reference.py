"""Seed helpers for reference NFL metadata and canonical mappings."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.models.espn import Team, Venue
from app.services.canonical import CanonicalPlayerReference, PlayerReconciliationService

_DATA_DIR = Path(__file__).resolve().parent / "data"


def _load_json(filename: str) -> Any:
    path = _DATA_DIR / filename
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def seed_reference_data(session: Session) -> dict[str, int]:
    """Insert or update baseline NFL teams and venues from captured data."""

    payload = _load_json("reference_data.json")
    teams_added = 0
    venues_added = 0

    for venue_data in payload.get("venues", []):
        venue_id = venue_data.get("venue_id")
        if not venue_id:
            continue
        venue = session.get(Venue, venue_id)
        if venue is None:
            venue = Venue(
                venue_id=venue_id,
                name=venue_data.get("name", "Unknown Venue"),
                city=venue_data.get("city", ""),
                state=venue_data.get("state", ""),
                roof_type=venue_data.get("roof_type"),
                surface=venue_data.get("surface"),
                lat=venue_data.get("latitude"),
                lon=venue_data.get("longitude"),
            )
            session.add(venue)
            venues_added += 1
        else:
            venue.name = venue_data.get("name", venue.name)
            venue.city = venue_data.get("city", venue.city)
            venue.state = venue_data.get("state", venue.state)
            venue.roof_type = venue_data.get("roof_type", venue.roof_type)
            venue.surface = venue_data.get("surface", venue.surface)
            venue.lat = venue_data.get("latitude", venue.lat)
            venue.lon = venue_data.get("longitude", venue.lon)

    for team_data in payload.get("teams", []):
        team_id = team_data.get("espn_team_id")
        if team_id is None:
            continue
        team = session.get(Team, team_id)
        colors = team_data.get("colors") or {}
        logos = team_data.get("logos") or []
        logos_payload = {"logos": logos} if logos else team.logos_json if team else {}

        if team is None:
            team = Team(
                espn_team_id=team_id,
                name=team_data.get("name", "Unknown Team"),
                abbr=team_data.get("abbr", "UNK"),
                colors_json=colors,
                logos_json=logos_payload,
            )
            session.add(team)
            teams_added += 1
        else:
            team.name = team_data.get("name", team.name)
            team.abbr = team_data.get("abbr", team.abbr)
            if colors:
                team.colors_json = colors
            if logos:
                team.logos_json = logos_payload

    return {"teams": teams_added, "venues": venues_added}


def seed_canonical_players(session: Session) -> int:
    """Apply curated canonical player mappings from repository data."""

    payload = _load_json("canonical_players.json")
    service = PlayerReconciliationService(session)
    references = [
        CanonicalPlayerReference(
            full_name=entry.get("full_name", ""),
            position=entry.get("position", ""),
            team_abbr=(entry.get("team_abbr") or None),
            yahoo_player_id=entry.get("yahoo_player_id"),
            espn_player_id=entry.get("espn_player_id"),
            confidence=float(entry.get("confidence", 1.0)),
            is_manual=True,
        )
        for entry in payload
    ]

    mappings = service.reconcile(references)
    return len(mappings)


__all__ = ["seed_reference_data", "seed_canonical_players"]
