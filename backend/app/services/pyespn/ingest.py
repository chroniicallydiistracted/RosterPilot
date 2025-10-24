"""Persist PyESPN-derived scoreboard and play-by-play data."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.espn import Drive, Event, EventState, Play, Team, Venue


@dataclass(slots=True)
class EventContext:
    season: int
    week: int
    start_ts: datetime
    status_name: str
    home_team: Team
    away_team: Team
    venue: Venue | None


@dataclass(slots=True)
class EventStateContext:
    status_type: dict[str, Any]
    competition: dict[str, Any]
    teams_by_home_away: dict[str, dict[str, Any]]
    situation: dict[str, Any]
    possession_abbr: str | None


class PyESPNIngestionService:
    """Normalize and upsert PyESPN JSON payloads into the database."""

    def __init__(self, session: Session) -> None:
        self.session = session

    # ------------------------------------------------------------------
    # Scoreboard ingestion
    # ------------------------------------------------------------------
    def ingest_scoreboard(self, payload: dict[str, Any]) -> list[str]:
        """Upsert teams, venues, events, and state snapshots from a scoreboard."""

        event_ids: list[str] = []
        events = payload.get("events", [])
        for event in events:
            try:
                event_id = str(event["id"])
            except KeyError:  # pragma: no cover - defensive guard
                continue
            event_ids.append(event_id)

            competition = (event.get("competitions") or [{}])[0]
            season = int(event.get("season", {}).get("year", datetime.now(tz=UTC).year))
            week = int(event.get("week", {}).get("number", 0))
            start_ts = _parse_datetime(competition.get("date") or event.get("date"))
            status_type = competition.get("status", {}).get("type", {})

            teams_by_home_away = _split_competitors(competition.get("competitors") or [])
            if not teams_by_home_away:
                continue

            home_team = self._upsert_team(teams_by_home_away["home"])
            away_team = self._upsert_team(teams_by_home_away["away"])
            venue = self._upsert_venue(competition.get("venue") or {})

            context = EventContext(
                season=season,
                week=week,
                start_ts=start_ts,
                status_name=status_type.get("name", "UNKNOWN"),
                home_team=home_team,
                away_team=away_team,
                venue=venue,
            )
            self._upsert_event(event_id=event_id, context=context)

            situation = competition.get("situation") or {}
            possession_id = situation.get("possession")
            possession_abbr = None
            if possession_id is not None:
                possession_team = _lookup_team_by_id(teams_by_home_away, str(possession_id))
                if possession_team:
                    team_payload = possession_team.get("team") or {}
                    possession_abbr = team_payload.get("abbreviation")

            state = self._ensure_event_state(event_id)
            state_context = EventStateContext(
                status_type=status_type,
                competition=competition,
                teams_by_home_away=teams_by_home_away,
                situation=situation,
                possession_abbr=possession_abbr,
            )
            self._update_event_state(state=state, context=state_context)

        return event_ids

    # ------------------------------------------------------------------
    # Play-by-play ingestion
    # ------------------------------------------------------------------
    def ingest_play_by_play(self, event_id: str, payload: dict[str, Any]) -> None:
        """Replace the drives/plays for a specific event with normalized rows."""

        drives_payload = payload.get("drives", {})
        drives = (drives_payload.get("current") or []) + (drives_payload.get("previous") or [])
        if not drives:
            return

        self.session.execute(delete(Play).where(Play.event_id == event_id))
        self.session.execute(delete(Drive).where(Drive.event_id == event_id))

        team_cache: dict[int, Team] = {}

        for drive in drives:
            drive_id = str(drive.get("id"))
            team_info = drive.get("team") or {}
            team_id = _safe_int(team_info.get("id"))
            if team_id is None:
                continue

            if team_id not in team_cache:
                team_cache[team_id] = self._ensure_team_from_drive(team_info)

            start = drive.get("start") or {}
            end = drive.get("end") or {}

            db_drive = Drive(
                event_id=event_id,
                drive_id=drive_id,
                team_id=team_id,
                start_yardline_100=_safe_int(start.get("yardsToEndzone")),
                end_yardline_100=_safe_int(end.get("yardsToEndzone")),
                result=drive.get("result") or drive.get("displayResult"),
                start_clock=_extract_clock(start),
                end_clock=_extract_clock(end),
            )
            self.session.add(db_drive)

            for play in drive.get("plays") or []:
                play_id = str(play.get("id"))
                if not play_id:
                    continue
                start_play = play.get("start") or {}
                play_row = Play(
                    event_id=event_id,
                    play_id=play_id,
                    drive_id=drive_id,
                    sequence=int(play.get("sequenceNumber", 0)),
                    clock=_extract_clock(play),
                    quarter=_safe_int((play.get("period") or {}).get("number")),
                    down=_safe_int(start_play.get("down")),
                    distance=_safe_int(start_play.get("distance")),
                    yardline_100=_safe_int(start_play.get("yardsToEndzone")),
                    type=_play_type(play),
                    yards=_safe_int(play.get("statYardage")),
                    raw_json=play,
                )
                self.session.add(play_row)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _upsert_team(self, competitor: dict[str, Any]) -> Team:
        team_info = competitor.get("team") or {}
        team_id = _safe_int(team_info.get("id"))
        if team_id is None:
            raise ValueError("Missing team id in competitor payload")

        team = self.session.get(Team, team_id)
        colors = {
            "primary": team_info.get("color"),
            "alternate": team_info.get("alternateColor"),
        }
        logos = _extract_logos(team_info)

        if team is None:
            team = Team(
                espn_team_id=team_id,
                name=team_info.get("displayName", team_info.get("name", "Unknown")),
                abbr=team_info.get("abbreviation", "UNK"),
                colors_json=colors,
                logos_json=logos,
            )
            self.session.add(team)
        else:
            team.name = team_info.get("displayName", team.name)
            team.abbr = team_info.get("abbreviation", team.abbr)
            team.colors_json = colors
            team.logos_json = logos if logos else team.logos_json
        return team

    def _ensure_team_from_drive(self, team_payload: dict[str, Any]) -> Team:
        team_id = _safe_int(team_payload.get("id"))
        if team_id is None:
            raise ValueError("Drive payload missing team id")
        team = self.session.get(Team, team_id)
        if team is None:
            # Drives payload includes richer logo sets - seed minimal placeholders.
            team = Team(
                espn_team_id=team_id,
                name=team_payload.get("displayName", team_payload.get("name", "Unknown")),
                abbr=team_payload.get("abbreviation", "UNK"),
                colors_json={"primary": None, "alternate": None},
                logos_json=_extract_logos(team_payload),
            )
            self.session.add(team)
        else:
            logos = _extract_logos(team_payload)
            if logos:
                team.logos_json = logos
        return team

    def _upsert_event(self, *, event_id: str, context: EventContext) -> Event:
        event = self.session.get(Event, event_id)
        if event is None:
            event = Event(
                event_id=event_id,
                season=context.season,
                week=context.week,
                start_ts=context.start_ts,
                status=context.status_name,
                home_id=context.home_team.espn_team_id,
                away_id=context.away_team.espn_team_id,
                venue_id=context.venue.venue_id if context.venue else None,
            )
            self.session.add(event)
            return event

        event.season = context.season
        event.week = context.week
        event.start_ts = context.start_ts
        if context.status_name:
            event.status = context.status_name
        event.home_id = context.home_team.espn_team_id
        event.away_id = context.away_team.espn_team_id
        event.venue_id = context.venue.venue_id if context.venue else None
        return event

    def _ensure_event_state(self, event_id: str) -> EventState:
        state = self.session.get(EventState, event_id)
        if state is None:
            state = EventState(event_id=event_id, broadcast_json={})
            self.session.add(state)
        return state

    def _update_event_state(self, *, state: EventState, context: EventStateContext) -> None:
        scoreboard_status = context.competition.get("status") or {}
        status_description = context.status_type.get("description")
        state.status = (
            status_description if isinstance(status_description, str) else "Final"
        )
        status_detail = context.status_type.get("shortDetail")
        state.status_detail = status_detail if isinstance(status_detail, str) else None
        state.quarter = scoreboard_status.get("period")
        state.clock = scoreboard_status.get("displayClock")
        state.possession = context.possession_abbr
        state.home_score = int(context.teams_by_home_away["home"].get("score", 0))
        state.away_score = int(context.teams_by_home_away["away"].get("score", 0))
        state.home_timeouts = context.situation.get("homeTimeouts")
        state.away_timeouts = context.situation.get("awayTimeouts")
        state.broadcast_json = _normalize_broadcasts(context.competition.get("broadcasts") or [])
        state.last_update = datetime.now(tz=UTC)

    def _upsert_venue(self, venue_payload: dict[str, Any]) -> Venue | None:
        venue_id = venue_payload.get("id")
        if venue_id is None:
            return None
        venue = self.session.get(Venue, str(venue_id))
        if venue is None:
            venue = Venue(
                venue_id=str(venue_id),
                name=venue_payload.get("fullName", "Unknown Venue"),
                city=(venue_payload.get("address") or {}).get("city", ""),
                state=(venue_payload.get("address") or {}).get("state", ""),
                roof_type="indoor" if venue_payload.get("indoor") else None,
                surface=venue_payload.get("surface"),
                lat=None,
                lon=None,
            )
            self.session.add(venue)
        else:
            venue.name = venue_payload.get("fullName", venue.name)
            address = venue_payload.get("address") or {}
            venue.city = address.get("city", venue.city)
            venue.state = address.get("state", venue.state)
            roof_type = "indoor" if venue_payload.get("indoor") else venue_payload.get("roofType")
            venue.roof_type = roof_type
            venue.surface = venue_payload.get("surface", venue.surface)
        return venue


# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------

def _parse_datetime(value: str | None) -> datetime:
    if not value:
        return datetime.now(tz=UTC)
    if value.endswith("Z"):
        value = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(value).astimezone(UTC)
    except ValueError:  # pragma: no cover - unexpected formats
        return datetime.now(tz=UTC)


def _split_competitors(competitors: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    buckets: dict[str, dict[str, Any]] = {}
    for competitor in competitors:
        side = competitor.get("homeAway")
        if side in {"home", "away"}:
            buckets[side] = competitor
    return buckets


def _lookup_team_by_id(
    competitors: dict[str, dict[str, Any]], team_id: str
) -> dict[str, Any] | None:
    for competitor in competitors.values():
        team_info = competitor.get("team") or {}
        if str(team_info.get("id")) == team_id:
            return competitor
    return None


def _normalize_broadcasts(broadcasts: list[dict[str, Any]]) -> dict[str, list[str]]:
    catalog: dict[str, list[str]] = defaultdict(list)
    for broadcast in broadcasts:
        media_type = broadcast.get("mediaType") or "tv"
        for name in broadcast.get("names") or []:
            catalog[media_type].append(name)
    # Provide consistent keys to simplify serialization
    return {
        "tv": catalog.get("tv", catalog.get("television", [])),
        "radio": catalog.get("radio", []),
        "stream": catalog.get("stream", catalog.get("digital", [])),
    }


def _extract_logos(source: dict[str, Any]) -> dict[str, Any]:
    logos = source.get("logos")
    if isinstance(logos, list) and logos:
        return {"logos": logos}
    logo = source.get("logo")
    return {"default": logo} if logo else {}


def _safe_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _extract_clock(source: dict[str, Any]) -> str | None:
    clock = source.get("clock") if isinstance(source, dict) else None
    if isinstance(clock, dict):
        return clock.get("displayValue") or clock.get("value")
    return clock


def _play_type(play: dict[str, Any]) -> str | None:
    type_info = play.get("type") or {}
    return type_info.get("text") or type_info.get("abbreviation")
