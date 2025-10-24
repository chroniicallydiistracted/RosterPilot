"""Unit tests covering the lineup optimizer helpers."""

from app.optimizer import (
    OptimizerPlayer,
    OptimizerSlot,
    eligible_positions_for_slot,
    is_reserve_slot,
    optimize_lineup,
    parse_player_positions,
)


def test_parse_player_positions_splits_tokens() -> None:
    positions = parse_player_positions("RB/WR,TE")
    assert positions == ("RB", "TE", "WR")


def test_eligible_positions_handles_aliases() -> None:
    available = {"QB", "RB", "WR", "TE"}
    flex_positions = eligible_positions_for_slot("Flex", available)
    assert flex_positions == {"RB", "WR", "TE"}

    rb_slot = eligible_positions_for_slot("RB1", available)
    assert rb_slot == {"RB"}


def test_is_reserve_slot_flags_bench_variants() -> None:
    assert is_reserve_slot("BENCH")
    assert is_reserve_slot("bn")
    assert is_reserve_slot("IR+")


def test_optimize_lineup_selects_highest_projection_assignment() -> None:
    players = [
        OptimizerPlayer(player_id="p1", name="Starter WR", positions=("WR",), projected_points=10.0),
        OptimizerPlayer(player_id="p2", name="Bench WR", positions=("WR",), projected_points=14.0),
        OptimizerPlayer(player_id="p3", name="Flex RB", positions=("RB",), projected_points=9.0),
    ]

    slots = [
        OptimizerSlot(slot_id="WR-0", slot_name="WR", eligible_positions=("WR",), current_player_id="p1"),
        OptimizerSlot(slot_id="FLEX-1", slot_name="FLEX", eligible_positions=("RB", "WR", "TE"), current_player_id="p3"),
    ]

    result = optimize_lineup(players, slots)
    assigned_players = {assignment.player_id for assignment in result.assignments}

    # Optimizer should promote the higher projected bench WR and slide the original starter to FLEX.
    assert assigned_players == {"p1", "p2"}
    assert result.total_points == 24.0
