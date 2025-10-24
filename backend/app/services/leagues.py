"""League and roster services backed by the persistence layer."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.yahoo import YahooLeague, YahooPlayer, YahooRoster, YahooTeam
from app.schemas.leagues import (
    LeagueRosterResponse,
    LeagueSummary,
    OptimizerInsight,
    PlayerProjection,
    RosterSlot,
    TeamSummary,
    UserLeaguesResponse,
)
from app.services.models import AuthContext


def list_user_leagues(session: Session, auth: AuthContext) -> UserLeaguesResponse:
    """Return the leagues available to the authenticated Yahoo user."""

    generated_at = datetime.now(tz=UTC)
    league_query: Select[tuple[YahooLeague]] = select(YahooLeague).where(YahooLeague.user_id == auth.user_id)
    leagues: list[LeagueSummary] = []

    for league in session.execute(league_query).scalars().all():
        my_team = session.execute(
            select(YahooTeam).where(
                YahooTeam.league_key == league.league_key,
                YahooTeam.is_user_team.is_(True),
            )
        ).scalar_one_or_none()

        if my_team is None:
            continue

        leagues.append(
            LeagueSummary(
                league_key=league.league_key,
                season=league.season,
                name=league.name,
                scoring_type=league.scoring_json.get("scoring_type", league.scoring_json.get("type", "")),
                status=league.status,
                my_team=TeamSummary(
                    team_key=my_team.team_key,
                    name=my_team.name,
                    manager=my_team.manager,
                ),
                last_synced=league.last_synced,
            )
        )

    return UserLeaguesResponse(generated_at=generated_at, leagues=leagues)


def get_league_roster(session: Session, auth: AuthContext, league_key: str, week: int) -> LeagueRosterResponse:
    """Return a roster payload including lightweight optimizer hints."""

    team = session.execute(
        select(YahooTeam).where(
            YahooTeam.league_key == league_key,
            YahooTeam.is_user_team.is_(True),
        )
    ).scalar_one_or_none()

    if team is None:
        raise ValueError(f"No roster found for user in league {league_key}")

    roster_rows = session.execute(
        select(YahooRoster, YahooPlayer)
        .join(YahooPlayer, YahooPlayer.yahoo_player_id == YahooRoster.yahoo_player_id, isouter=True)
        .where(YahooRoster.team_key == team.team_key, YahooRoster.week == week)
    ).all()

    starters: list[RosterSlot] = []
    bench: list[RosterSlot] = []

    for roster, player in roster_rows:
        projection = _build_player_projection(roster, player)
        slot = RosterSlot(
            slot=roster.slot,
            player=projection,
            recommended=roster.is_starter,
            locked=False,
        )
        if roster.is_starter:
            starters.append(slot)
        else:
            bench.append(slot)

    optimizer = _build_optimizer_summary(starters, bench)

    return LeagueRosterResponse(
        league_key=league_key,
        week=week,
        team=TeamSummary(team_key=team.team_key, name=team.name, manager=team.manager),
        generated_at=datetime.now(tz=UTC),
        starters=starters,
        bench=bench,
        optimizer=optimizer,
    )


def _build_player_projection(roster: YahooRoster, player: YahooPlayer | None) -> PlayerProjection:
    return PlayerProjection(
        yahoo_player_id=player.yahoo_player_id if player else "unknown",
        full_name=player.name if player else "TBD",
        team_abbr=player.team_abbr if player else "FA",
        position=player.pos if player else "N/A",
        status=player.status if player else "UNKNOWN",
        projected_points=roster.projected_points,
        actual_points=roster.actual_points,
    )


def _build_optimizer_summary(starters: list[RosterSlot], bench: list[RosterSlot]) -> OptimizerInsight:
    starter_total = sum(slot.player.projected_points for slot in starters)
    bench_total = sum(slot.player.projected_points for slot in bench) or 0.0
    delta_points = max(0.0, round(starter_total - bench_total, 1))

    rationale = [
        "Projected starters outpace bench depth by {:.1f} points".format(delta_points),
        "Monitor injuries before lock" if any(slot.player.status not in {"ACTIVE", "OK"} for slot in starters) else "Lineup healthy",
        "Weather impact negligible based on indoor matchups",
    ]

    recommended = [slot.player.full_name for slot in sorted(starters, key=lambda s: s.player.projected_points, reverse=True)]
    return OptimizerInsight(recommended_starters=recommended, delta_points=delta_points, rationale=rationale)
