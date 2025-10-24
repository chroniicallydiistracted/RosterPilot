"""Stub implementations for Yahoo league and roster workflows."""

from __future__ import annotations

from datetime import UTC, datetime

from app.schemas.leagues import (
    LeagueRosterResponse,
    OptimizerInsight,
    PlayerProjection,
    RosterSlot,
    TeamSummary,
    UserLeaguesResponse,
)


def get_user_leagues_stub() -> UserLeaguesResponse:
    """Return a deterministic set of leagues for contract testing."""

    generated_at = datetime.now(tz=UTC)
    leagues = [
        {
            "league_key": "nfl.l.12345",
            "season": 2024,
            "name": "RosterPilot Analytics League",
            "scoring_type": "points_per_reception",
            "status": "in_season",
            "my_team": {
                "team_key": "nfl.l.12345.t.1",
                "name": "Phoenix Firebirds",
                "manager": "Taylor Jenkins",
            },
            "source": "yahoo",
            "last_synced": generated_at,
        },
        {
            "league_key": "nfl.l.98765",
            "season": 2024,
            "name": "Data Wizards Dynasty",
            "scoring_type": "half_ppr",
            "status": "pre_draft",
            "my_team": {
                "team_key": "nfl.l.98765.t.3",
                "name": "Desert Analytics",
                "manager": "Taylor Jenkins",
            },
            "source": "yahoo",
            "last_synced": generated_at,
        },
    ]

    return UserLeaguesResponse.model_validate({"generated_at": generated_at, "leagues": leagues})


def get_league_roster_stub(league_key: str, week: int) -> LeagueRosterResponse:
    """Return a mock roster response with optimizer rationale."""

    generated_at = datetime.now(tz=UTC)

    starters = [
        RosterSlot(
            slot="QB",
            player=PlayerProjection(
                yahoo_player_id="257654",
                full_name="Jalen Hurts",
                team_abbr="PHI",
                position="QB",
                status="ACTIVE",
                projected_points=24.3,
                actual_points=None,
            ),
            recommended=True,
            locked=False,
        ),
        RosterSlot(
            slot="RB1",
            player=PlayerProjection(
                yahoo_player_id="272569",
                full_name="Bijan Robinson",
                team_abbr="ATL",
                position="RB",
                status="ACTIVE",
                projected_points=18.7,
                actual_points=None,
            ),
            recommended=True,
            locked=False,
        ),
        RosterSlot(
            slot="WR1",
            player=PlayerProjection(
                yahoo_player_id="2482202",
                full_name="Amon-Ra St. Brown",
                team_abbr="DET",
                position="WR",
                status="QUESTIONABLE",
                projected_points=17.9,
                actual_points=None,
            ),
            recommended=True,
            locked=False,
        ),
    ]

    bench = [
        RosterSlot(
            slot="BENCH",
            player=PlayerProjection(
                yahoo_player_id="301234",
                full_name="James Conner",
                team_abbr="ARI",
                position="RB",
                status="ACTIVE",
                projected_points=11.2,
                actual_points=None,
            ),
            recommended=False,
            locked=False,
        ),
        RosterSlot(
            slot="BENCH",
            player=PlayerProjection(
                yahoo_player_id="278998",
                full_name="Jordan Addison",
                team_abbr="MIN",
                position="WR",
                status="ACTIVE",
                projected_points=10.4,
                actual_points=None,
            ),
            recommended=False,
            locked=False,
        ),
    ]

    optimizer = OptimizerInsight(
        recommended_starters=[slot.player.full_name for slot in starters],
        delta_points=8.6,
        rationale=[
            "Higher median projection versus current lineup",
            "Favorable pace-of-play matchup",
            "Weather impact negligible (indoor venue)",
        ],
        source="optimizer",
    )

    return LeagueRosterResponse(
        league_key=league_key,
        week=week,
        team=TeamSummary(
            team_key="nfl.l.12345.t.1",
            name="Phoenix Firebirds",
            manager="Taylor Jenkins",
        ),
        generated_at=generated_at,
        starters=starters,
        bench=bench,
        optimizer=optimizer,
    )
