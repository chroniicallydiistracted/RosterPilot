"""Stub implementations for PyESPN-driven game data."""

from __future__ import annotations

from datetime import UTC, datetime

from app.schemas.games import (
    DriveSummary,
    LiveGamesResponse,
    PlayByPlayResponse,
    PlayDetail,
    TeamGameState,
)


def get_live_games_stub() -> LiveGamesResponse:
    """Return a deterministic set of live game summaries."""

    generated_at = datetime.now(tz=UTC)
    games = [
        {
            "event_id": "401547634",
            "season": 2024,
            "week": 7,
            "status": "IN_PROGRESS",
            "quarter": 3,
            "clock": "07:42",
            "possession": "PHI",
            "venue": {
                "venue_id": "3794",
                "name": "State Farm Stadium",
                "city": "Glendale",
                "state": "AZ",
            },
            "home": {
                "espn_team_id": 22,
                "name": "Arizona Cardinals",
                "abbr": "ARI",
                "score": 17,
                "timeouts": 2,
            },
            "away": {
                "espn_team_id": 21,
                "name": "Philadelphia Eagles",
                "abbr": "PHI",
                "score": 24,
                "timeouts": 3,
            },
            "last_update": generated_at,
            "broadcast": {
                "tv": "FOX",
                "radio": ["Eagles Radio Network", "Arizona Sports 98.7"],
            },
            "source": "pyespn",
        }
    ]

    return LiveGamesResponse.model_validate({"generated_at": generated_at, "games": games})


def get_play_by_play_stub(event_id: str) -> PlayByPlayResponse:
    """Return a deterministic play-by-play timeline for integration tests."""

    generated_at = datetime.now(tz=UTC)

    drives = [
        DriveSummary(
            drive_id="1",
            team=TeamGameState(
                espn_team_id=21,
                name="Philadelphia Eagles",
                abbr="PHI",
                score=7,
            ),
            result="Touchdown",
            start_clock="15:00",
            end_clock="11:35",
            plays=[
                PlayDetail(
                    play_id="1",
                    sequence=1,
                    clock="15:00",
                    quarter=1,
                    down=1,
                    distance=10,
                    yardline_100=75,
                    type="kickoff",
                    yards=25,
                    description="J. Elliott kickoff returned 25 yards to PHI 25.",
                    flags=[],
                ),
                PlayDetail(
                    play_id="5",
                    sequence=2,
                    clock="13:48",
                    quarter=1,
                    down=2,
                    distance=6,
                    yardline_100=69,
                    type="pass",
                    yards=12,
                    description="J. Hurts pass short right to D. Smith for 12 yards.",
                    flags=[],
                ),
                PlayDetail(
                    play_id="12",
                    sequence=3,
                    clock="11:35",
                    quarter=1,
                    down=1,
                    distance=10,
                    yardline_100=10,
                    type="rush",
                    yards=10,
                    description="J. Hurts rush to ARI 0 for 10 yards, TOUCHDOWN.",
                    flags=["TD"],
                ),
            ],
        ),
        DriveSummary(
            drive_id="2",
            team=TeamGameState(
                espn_team_id=22,
                name="Arizona Cardinals",
                abbr="ARI",
                score=3,
            ),
            result="Field Goal",
            start_clock="11:35",
            end_clock="06:02",
            plays=[
                PlayDetail(
                    play_id="20",
                    sequence=1,
                    clock="11:30",
                    quarter=1,
                    down=1,
                    distance=10,
                    yardline_100=75,
                    type="pass",
                    yards=18,
                    description="K. Murray pass deep left to M. Wilson for 18 yards.",
                    flags=[],
                ),
                PlayDetail(
                    play_id="29",
                    sequence=4,
                    clock="06:12",
                    quarter=1,
                    down=3,
                    distance=7,
                    yardline_100=15,
                    type="pass",
                    yards=5,
                    description="K. Murray pass short middle to T. McBride for 5 yards.",
                    flags=[],
                ),
                PlayDetail(
                    play_id="31",
                    sequence=5,
                    clock="06:02",
                    quarter=1,
                    down=None,
                    distance=None,
                    yardline_100=10,
                    type="field_goal",
                    yards=27,
                    description="M. Prater 27 yard field goal is GOOD.",
                    flags=["FG"],
                ),
            ],
        ),
    ]

    return PlayByPlayResponse(
        event_id=event_id,
        generated_at=generated_at,
        drives=drives,
        source="pyespn",
    )
