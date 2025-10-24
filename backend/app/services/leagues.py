"""League and roster services backed by the persistence layer."""

from __future__ import annotations

from datetime import UTC, datetime
from itertools import count

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.yahoo import YahooLeague, YahooPlayer, YahooRoster, YahooTeam
from app.optimizer import (
    OptimizerAssignment,
    OptimizerPlayer,
    OptimizerResult,
    OptimizerSlot,
    eligible_positions_for_slot,
    is_reserve_slot,
    optimize_lineup,
    parse_player_positions,
)
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

    roster_result = (
        session.execute(
            select(YahooRoster, YahooPlayer)
            .join(
                YahooPlayer,
                YahooPlayer.yahoo_player_id == YahooRoster.yahoo_player_id,
                isouter=True,
            )
            .where(YahooRoster.team_key == team.team_key, YahooRoster.week == week)
        )
        .tuples()
        .all()
    )
    roster_rows: list[tuple[YahooRoster, YahooPlayer | None]] = [
        (roster, player) for roster, player in roster_result
    ]

    (
        starters,
        bench,
        optimizer,
    ) = _build_roster_payload(roster_rows)

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


def _build_roster_payload(
    roster_rows: list[tuple[YahooRoster, YahooPlayer | None]]
) -> tuple[list[RosterSlot], list[RosterSlot], OptimizerInsight]:
    """Transform database rows into API response payloads with optimizer output."""

    player_projections: dict[str, PlayerProjection] = {}
    optimizer_players: dict[str, OptimizerPlayer] = {}
    available_positions: set[str] = set()
    player_status: dict[str, str | None] = {}
    player_slot_lookup: dict[str, str] = {}

    for roster, player in roster_rows:
        if player is None or roster.yahoo_player_id is None:
            continue

        projection = _build_player_projection(roster, player)
        player_projections[roster.yahoo_player_id] = projection
        player_slot_lookup[roster.yahoo_player_id] = roster.slot
        player_status[roster.yahoo_player_id] = projection.status

        positions = parse_player_positions(player.pos)
        if not positions:
            positions = (player.pos.upper(),)
        available_positions.update(positions)

        if roster.yahoo_player_id not in optimizer_players:
            optimizer_players[roster.yahoo_player_id] = OptimizerPlayer(
                player_id=roster.yahoo_player_id,
                name=projection.full_name,
                positions=positions,
                projected_points=projection.projected_points,
                status=projection.status,
            )

    if not available_positions:
        available_positions.update({"QB", "RB", "WR", "TE", "K", "DEF"})

    active_slots: list[OptimizerSlot] = []
    slot_metadata: list[tuple[OptimizerSlot, str | None]] = []
    slot_index = count()

    for roster, player in roster_rows:
        slot_name = roster.slot
        if is_reserve_slot(slot_name):
            continue

        slot_id = f"{slot_name}-{next(slot_index)}"
        eligible_positions = tuple(sorted(eligible_positions_for_slot(slot_name, available_positions)))
        slot = OptimizerSlot(
            slot_id=slot_id,
            slot_name=slot_name,
            eligible_positions=eligible_positions,
            current_player_id=roster.yahoo_player_id,
        )
        active_slots.append(slot)
        slot_metadata.append((slot, roster.yahoo_player_id))

    optimizer_result = optimize_lineup(optimizer_players.values(), active_slots)
    recommended_ids = optimizer_result.recommended_player_ids

    assignment_map = {assignment.slot_id: assignment for assignment in optimizer_result.assignments}
    starters: list[RosterSlot] = []

    for slot, current_player_id in slot_metadata:
        assignment = assignment_map.get(slot.slot_id)
        if assignment is None:
            if current_player_id and current_player_id in player_projections:
                projection = player_projections[current_player_id]
                starters.append(
                    RosterSlot(
                        slot=slot.slot_name,
                        player=projection,
                        recommended=False,
                        locked=False,
                    )
                )
            continue
        projection = player_projections.get(assignment.player_id)
        if projection is None:
            continue
        starters.append(
            RosterSlot(
                slot=slot.slot_name,
                player=projection,
                recommended=True,
                locked=False,
            )
        )

    bench: list[RosterSlot] = []
    for player_id, projection in player_projections.items():
        if player_id in recommended_ids:
            continue
        bench_slot = player_slot_lookup.get(player_id, "BENCH")
        bench.append(
            RosterSlot(
                slot=bench_slot,
                player=projection,
                recommended=False,
                locked=False,
            )
        )

    bench.sort(key=lambda slot: slot.player.projected_points, reverse=True)

    optimizer = _build_optimizer_summary(
        slot_metadata=slot_metadata,
        assignment_map=assignment_map,
        player_projections=player_projections,
        player_status=player_status,
        optimizer_result=optimizer_result,
    )

    return starters, bench, optimizer


def _build_optimizer_summary(
    *,
    slot_metadata: list[tuple[OptimizerSlot, str | None]],
    assignment_map: dict[str, OptimizerAssignment],
    player_projections: dict[str, PlayerProjection],
    player_status: dict[str, str | None],
    optimizer_result: OptimizerResult,
) -> OptimizerInsight:
    """Compose the OptimizerInsight payload from solver results."""

    current_total = 0.0
    recommended_names: list[str] = []
    recommended_statuses: list[str | None] = []
    rationale: list[str] = []
    changes: list[tuple[float, str]] = []

    for slot, current_player_id in slot_metadata:
        assignment = assignment_map.get(slot.slot_id)
        if current_player_id and current_player_id in player_projections:
            current_total += player_projections[current_player_id].projected_points
        if assignment:
            projection = player_projections.get(assignment.player_id)
            if projection:
                recommended_names.append(projection.full_name)
                recommended_statuses.append(projection.status)

        if assignment and current_player_id and assignment.player_id != current_player_id:
            new_player = player_projections.get(assignment.player_id)
            current_player = player_projections.get(current_player_id)
            if new_player and current_player:
                gain = new_player.projected_points - current_player.projected_points
                description = (
                    f"{slot.slot_name}: start {new_player.full_name} ({new_player.projected_points:.1f}) "
                    f"over {current_player.full_name} ({current_player.projected_points:.1f}) for +{gain:.1f} pts"
                )
                changes.append((gain, description))

    optimized_total = optimizer_result.total_points
    raw_delta = optimized_total - current_total
    delta_points = round(max(0.0, raw_delta), 1)

    rationale.append(
        "Optimizer projects {:.1f} pts vs current {:.1f} pts (Δ {:.1f}).".format(
            optimized_total,
            current_total,
            raw_delta,
        )
    )

    for _, description in sorted(changes, key=lambda item: item[0], reverse=True)[:2]:
        rationale.append(description)

    if raw_delta <= 0 and not changes:
        rationale.append("Current lineup already optimal based on projections.")

    for name, status in zip(recommended_names, recommended_statuses):
        if status and status not in {"ACTIVE", "OK"}:
            rationale.append(f"Monitor {name} ({status.lower()}) before lineup lock.")
            break

    if optimizer_result.fallback_used:
        rationale.append("Greedy fallback used because CP-SAT solver was unavailable.")

    return OptimizerInsight(
        recommended_starters=recommended_names,
        delta_points=delta_points,
        rationale=rationale,
    )
