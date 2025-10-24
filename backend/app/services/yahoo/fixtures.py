"""Static Yahoo fixture payloads used for the scaffold and tests."""

from __future__ import annotations

from datetime import UTC, datetime

from app.services.yahoo.models import (
    YahooLeagueData,
    YahooPlayerData,
    YahooRosterEntry,
    YahooTeamData,
    YahooUserBundle,
)


def load_test_user_bundle() -> YahooUserBundle:
    """Return a deterministic Yahoo bundle used across tests."""

    last_synced = datetime(2024, 8, 28, 14, 0, tzinfo=UTC)

    phoenix_roster = [
        YahooRosterEntry(
            week=7,
            slot="QB",
            is_starter=True,
            player=YahooPlayerData(
                yahoo_player_id="257654",
                full_name="Jalen Hurts",
                position="QB",
                team_abbr="PHI",
                status="ACTIVE",
                bye_week=10,
                projected_points=24.3,
                actual_points=None,
            ),
        ),
        YahooRosterEntry(
            week=7,
            slot="RB1",
            is_starter=True,
            player=YahooPlayerData(
                yahoo_player_id="272569",
                full_name="Bijan Robinson",
                position="RB",
                team_abbr="ATL",
                status="ACTIVE",
                bye_week=12,
                projected_points=18.7,
                actual_points=None,
            ),
        ),
        YahooRosterEntry(
            week=7,
            slot="WR1",
            is_starter=True,
            player=YahooPlayerData(
                yahoo_player_id="2482202",
                full_name="Amon-Ra St. Brown",
                position="WR",
                team_abbr="DET",
                status="QUESTIONABLE",
                bye_week=9,
                projected_points=17.9,
                actual_points=None,
            ),
        ),
        YahooRosterEntry(
            week=7,
            slot="FLEX",
            is_starter=True,
            player=YahooPlayerData(
                yahoo_player_id="301234",
                full_name="James Conner",
                position="RB",
                team_abbr="ARI",
                status="ACTIVE",
                bye_week=11,
                projected_points=13.5,
                actual_points=None,
            ),
        ),
        YahooRosterEntry(
            week=7,
            slot="BENCH",
            is_starter=False,
            player=YahooPlayerData(
                yahoo_player_id="278998",
                full_name="Jordan Addison",
                position="WR",
                team_abbr="MIN",
                status="ACTIVE",
                bye_week=13,
                projected_points=10.4,
                actual_points=None,
            ),
        ),
    ]

    phoenix_team = YahooTeamData(
        team_key="nfl.l.12345.t.1",
        name="Phoenix Firebirds",
        manager="Taylor Jenkins",
        is_user_team=True,
        roster=phoenix_roster,
    )

    rival_team = YahooTeamData(
        team_key="nfl.l.12345.t.2",
        name="Bay Area Algorithms",
        manager="Jordan Lee",
        is_user_team=False,
        roster=[],
    )

    analytics_league = YahooLeagueData(
        league_key="nfl.l.12345",
        season=2024,
        name="RosterPilot Analytics League",
        scoring_type="points_per_reception",
        status="in_season",
        scoring_json={"scoring_type": "ppr", "roster_slots": ["QB", "RB", "WR", "FLEX", "BENCH"]},
        last_synced=last_synced,
        teams=[phoenix_team, rival_team],
    )

    dynasty_league = YahooLeagueData(
        league_key="nfl.l.98765",
        season=2024,
        name="Data Wizards Dynasty",
        scoring_type="half_ppr",
        status="pre_draft",
        scoring_json={"scoring_type": "half_ppr", "keepers": True},
        last_synced=last_synced,
        teams=[
            YahooTeamData(
                team_key="nfl.l.98765.t.3",
                name="Desert Analytics",
                manager="Taylor Jenkins",
                is_user_team=True,
                roster=[],
            )
        ],
    )

    return YahooUserBundle(
        yahoo_sub="demo-sub-123",
        yahoo_guid="demo-guid-456",
        profile_nickname="Taylor",
        leagues=[analytics_league, dynasty_league],
    )
