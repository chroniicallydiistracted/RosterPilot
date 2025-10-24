"""Query helpers that surface PyESPN-backed game data."""

from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session, aliased

from app.models.espn import Drive, Event, EventState, Play, Team, Venue
from app.schemas.games import (
    DriveSummary,
    LiveGamesResponse,
    LiveGameSummary,
    PlayByPlayResponse,
    PlayDetail,
    TeamGameState,
    VenueInfo,
)


def list_live_games(session: Session) -> LiveGamesResponse:
    """Return the scoreboard snapshot for all ingested events."""

    generated_at = datetime.now(tz=UTC)
    home_team = aliased(Team)
    away_team = aliased(Team)

    stmt = (
        select(Event, EventState, home_team, away_team, Venue)
        .join(EventState, EventState.event_id == Event.event_id)
        .join(home_team, home_team.espn_team_id == Event.home_id)
        .join(away_team, away_team.espn_team_id == Event.away_id)
        .join(Venue, Venue.venue_id == Event.venue_id, isouter=True)
        .order_by(Event.start_ts)
    )

    games: list[LiveGameSummary] = []
    for event, state, home, away, venue in session.execute(stmt):
        games.append(
            LiveGameSummary(
                event_id=event.event_id,
                season=event.season,
                week=event.week,
                status=state.status,
                quarter=state.quarter,
                clock=state.clock,
                possession=state.possession,
                venue=_venue_info(venue),
                home=_team_game_state(home, state.home_score, state.home_timeouts),
                away=_team_game_state(away, state.away_score, state.away_timeouts),
                last_update=state.last_update,
                broadcast=_broadcast_payload(state.broadcast_json),
            )
        )

    return LiveGamesResponse(generated_at=generated_at, games=games)


def get_play_by_play(session: Session, event_id: str) -> PlayByPlayResponse:
    """Build the normalized play-by-play timeline for an event."""

    event_row = session.execute(
        select(Event, EventState)
        .join(EventState, EventState.event_id == Event.event_id)
        .where(Event.event_id == event_id)
    ).one_or_none()

    if event_row is None:
        raise ValueError(f"Unknown event_id {event_id}")
    event, state = event_row

    home_team = session.get(Team, event.home_id)
    away_team = session.get(Team, event.away_id)
    if home_team is None or away_team is None:
        raise ValueError("Missing team metadata for event")

    drives = list(
        session.execute(
        select(Drive).where(Drive.event_id == event_id).order_by(Drive.drive_id)
    ).scalars()
    )
    plays = list(
        session.execute(
        select(Play).where(Play.event_id == event_id).order_by(Play.drive_id, Play.sequence)
    ).scalars()
    )

    plays_by_drive: dict[str, list[Play]] = defaultdict(list)
    for play in plays:
        plays_by_drive[play.drive_id].append(play)

    drive_payloads: list[DriveSummary] = []
    for drive in drives:
        team = _resolve_drive_team(drive.team_id, home_team, away_team)
        team_state = _team_game_state(
            team,
            state.home_score if team.espn_team_id == home_team.espn_team_id else state.away_score,
            state.home_timeouts if team.espn_team_id == home_team.espn_team_id else state.away_timeouts,
        )
        drive_payloads.append(
            DriveSummary(
                drive_id=drive.drive_id,
                team=team_state,
                result=drive.result or "Unknown",
                start_clock=drive.start_clock or "0:00",
                end_clock=drive.end_clock or drive.start_clock or "0:00",
                plays=[_play_detail(play) for play in plays_by_drive.get(drive.drive_id, [])],
            )
        )

    return PlayByPlayResponse(
        event_id=event_id,
        generated_at=datetime.now(tz=UTC),
        drives=drive_payloads,
    )


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------


def _team_game_state(team: Team, score: int, timeouts: int | None) -> TeamGameState:
    return TeamGameState(
        espn_team_id=team.espn_team_id,
        name=team.name,
        abbr=team.abbr,
        score=score,
        timeouts=timeouts,
    )


def _venue_info(venue: Venue | None) -> VenueInfo:
    if venue is None:
        return VenueInfo(venue_id="unknown", name="Unknown", city="", state="")
    return VenueInfo(
        venue_id=venue.venue_id,
        name=venue.name,
        city=venue.city,
        state=venue.state,
    )


def _broadcast_payload(data: dict[str, Iterable[str]] | None) -> dict[str, list[str]]:
    if not data:
        return {"tv": [], "radio": [], "stream": []}
    return {
        "tv": list(data.get("tv", [])),
        "radio": list(data.get("radio", [])),
        "stream": list(data.get("stream", [])),
    }


def _resolve_drive_team(team_id: int | None, home: Team, away: Team) -> Team:
    if team_id == home.espn_team_id:
        return home
    if team_id == away.espn_team_id:
        return away
    # Fall back to home team if PyESPN omits the identifier.
    return home


def _play_detail(play: Play) -> PlayDetail:
    raw = play.raw_json or {}
    quarter = play.quarter or (raw.get("period") or {}).get("number") or 1
    clock = play.clock or (raw.get("clock") or {}).get("displayValue") or "0:00"
    type_text = play.type or (raw.get("type") or {}).get("text") or "Unknown"

    flags: list[str] = []
    if raw.get("scoringPlay"):
        flags.append("SCORING")
    abbr = (raw.get("type") or {}).get("abbreviation")
    if abbr:
        flags.append(abbr)

    down = play.down if play.down and play.down > 0 else None
    distance = play.distance if play.distance and play.distance > 0 else None

    return PlayDetail(
        play_id=play.play_id,
        sequence=play.sequence,
        clock=clock,
        quarter=quarter,
        down=down,
        distance=distance,
        yardline_100=play.yardline_100,
        type=type_text,
        yards=play.yards,
        description=raw.get("text", ""),
        flags=sorted(set(flags)),
    )
