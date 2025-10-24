"""Optimization engine that selects the highest scoring lineup."""

from __future__ import annotations

from typing import Iterable

from app.optimizer.models import (
    OptimizerAssignment,
    OptimizerPlayer,
    OptimizerResult,
    OptimizerSlot,
)


def optimize_lineup(
    players: Iterable[OptimizerPlayer],
    slots: Iterable[OptimizerSlot],
) -> OptimizerResult:
    """Compute the optimal lineup using CP-SAT with a greedy fallback."""

    player_list = list(players)
    slot_list = list(slots)

    if not player_list or not slot_list:
        return OptimizerResult(assignments=tuple(), total_points=0.0, fallback_used=True)

    try:
        return _solve_with_cp_sat(player_list, slot_list)
    except Exception:  # pragma: no cover - exercised when ortools unavailable
        return _solve_with_greedy(player_list, slot_list)


def _solve_with_cp_sat(
    players: list[OptimizerPlayer],
    slots: list[OptimizerSlot],
) -> OptimizerResult:
    from ortools.sat.python import cp_model  # type: ignore

    model = cp_model.CpModel()
    variables: dict[tuple[int, int], cp_model.IntVar] = {}
    player_indices = {player.player_id: idx for idx, player in enumerate(players)}

    for slot_idx, slot in enumerate(slots):
        eligible_indices = [
            player_indices[player.player_id]
            for player in players
            if set(player.positions) & set(slot.eligible_positions)
        ]

        # If we cannot determine eligibility for a slot, allow all players.
        if not eligible_indices:
            eligible_indices = list(player_indices.values())

        slot_vars = []
        for player_index in eligible_indices:
            var = model.NewBoolVar(f"slot_{slot_idx}_player_{player_index}")
            variables[(slot_idx, player_index)] = var
            slot_vars.append(var)

        model.Add(sum(slot_vars) == 1)

    for player_index in player_indices.values():
        player_vars = [
            variables[(slot_idx, player_index)]
            for slot_idx in range(len(slots))
            if (slot_idx, player_index) in variables
        ]
        if player_vars:
            model.Add(sum(player_vars) <= 1)

    objective_terms = []
    scaling_factor = 1000
    for slot_idx, slot in enumerate(slots):
        for player_index, player in enumerate(players):
            key = (slot_idx, player_index)
            if key not in variables:
                continue
            weight = int(round(player.projected_points * scaling_factor))
            objective_terms.append(variables[key] * weight)

    model.Maximize(sum(objective_terms))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 2.0
    solver.parameters.num_search_workers = 8
    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return _solve_with_greedy(players, slots)

    assignments: list[OptimizerAssignment] = []
    for slot_idx, slot in enumerate(slots):
        chosen_player: OptimizerPlayer | None = None
        for player_index, player in enumerate(players):
            key = (slot_idx, player_index)
            if key not in variables:
                continue
            if solver.Value(variables[key]) == 1:
                chosen_player = player
                break
        if chosen_player is None:
            # Fallback to the highest projected player for the slot.
            eligible_players = [
                player
                for player in players
                if set(player.positions) & set(slot.eligible_positions)
            ]
            if not eligible_players:
                eligible_players = players
            chosen_player = max(eligible_players, key=lambda p: p.projected_points)

        assignments.append(
            OptimizerAssignment(
                slot_id=slot.slot_id,
                slot_name=slot.slot_name,
                player_id=chosen_player.player_id,
                projected_points=chosen_player.projected_points,
            )
        )

    total_points = sum(assignment.projected_points for assignment in assignments)
    return OptimizerResult(assignments=tuple(assignments), total_points=total_points)


def _solve_with_greedy(
    players: list[OptimizerPlayer],
    slots: list[OptimizerSlot],
) -> OptimizerResult:
    remaining_players = players.copy()
    assignments: list[OptimizerAssignment] = []

    for slot in slots:
        eligible_players = [
            player
            for player in remaining_players
            if set(player.positions) & set(slot.eligible_positions)
        ]
        if not eligible_players:
            eligible_players = remaining_players

        if not eligible_players:
            break

        chosen_player = max(eligible_players, key=lambda p: p.projected_points)
        assignments.append(
            OptimizerAssignment(
                slot_id=slot.slot_id,
                slot_name=slot.slot_name,
                player_id=chosen_player.player_id,
                projected_points=chosen_player.projected_points,
            )
        )
        remaining_players = [player for player in remaining_players if player.player_id != chosen_player.player_id]

    total_points = sum(assignment.projected_points for assignment in assignments)
    return OptimizerResult(assignments=tuple(assignments), total_points=total_points, fallback_used=True)

