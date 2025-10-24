"""Slot and position normalization helpers for the optimizer."""

from __future__ import annotations

import re
from functools import lru_cache

# Slot tokens that indicate the player is not eligible for the starting optimization.
RESERVE_SLOT_PREFIXES = (
    "BENCH",
    "BN",
    "RESERVE",
    "RES",
    "IR",
    "PUP",
    "NFI",
    "COVID",
    "TAXI",
)


POSITION_SYNONYMS: dict[str, str] = {
    "W": "WR",
    "R": "RB",
    "T": "TE",
    "Q": "QB",
    "QB": "QB",
    "RB": "RB",
    "WR": "WR",
    "TE": "TE",
    "K": "K",
    "PK": "K",
    "DST": "DEF",
    "D/ST": "DEF",
    "DEF": "DEF",
    "DL": "DL",
    "DE": "DL",
    "DT": "DL",
    "LB": "LB",
    "EDGE": "DL",
    "DB": "DB",
    "CB": "DB",
    "S": "DB",
    "IDP": "IDP",
}


SLOT_OVERRIDES: dict[str, set[str]] = {
    "FLEX": {"RB", "WR", "TE"},
    "W/R": {"WR", "RB"},
    "R/W": {"WR", "RB"},
    "W/T": {"WR", "TE"},
    "WR/RB": {"WR", "RB"},
    "RB/WR": {"WR", "RB"},
    "WR/TE": {"WR", "TE"},
    "RB/WR/TE": {"RB", "WR", "TE"},
    "W/R/T": {"WR", "RB", "TE"},
    "SUPERFLEX": {"QB", "RB", "WR", "TE"},
    "SUPER FLEX": {"QB", "RB", "WR", "TE"},
    "OP": {"QB", "RB", "WR", "TE"},
    "Q/W/R": {"QB", "WR", "RB"},
    "Q/W/R/T": {"QB", "WR", "RB", "TE"},
    "WR": {"WR"},
    "WR1": {"WR"},
    "WR2": {"WR"},
    "WR3": {"WR"},
    "RB": {"RB"},
    "RB1": {"RB"},
    "RB2": {"RB"},
    "RB3": {"RB"},
    "TE": {"TE"},
    "TE1": {"TE"},
    "QB": {"QB"},
    "QB1": {"QB"},
}


@lru_cache(maxsize=None)
def normalize_slot_name(slot_name: str) -> str:
    """Normalize a roster slot name for comparison."""

    cleaned = re.sub(r"[^A-Z/]+", "", slot_name.upper())
    return cleaned


def is_reserve_slot(slot_name: str) -> bool:
    """Return True if the slot is a bench or reserve position."""

    normalized = slot_name.strip().upper().replace(" ", "")
    return any(normalized.startswith(prefix) for prefix in RESERVE_SLOT_PREFIXES)


def parse_player_positions(position_string: str) -> tuple[str, ...]:
    """Split a Yahoo position string into canonical tokens."""

    tokens = re.split(r"[\s/,]+", position_string.upper())
    normalized: set[str] = set()
    for token in tokens:
        if not token:
            continue
        normalized_token = POSITION_SYNONYMS.get(token, token)
        normalized.add(normalized_token)
    return tuple(sorted(normalized))


def eligible_positions_for_slot(slot_name: str, available_positions: set[str]) -> set[str]:
    """Return the set of eligible positions for a roster slot."""

    normalized_slot = normalize_slot_name(slot_name)
    if normalized_slot in SLOT_OVERRIDES:
        return SLOT_OVERRIDES[normalized_slot]

    if "/" in normalized_slot:
        tokens = normalized_slot.split("/")
        eligible = {
            POSITION_SYNONYMS.get(token, token)
            for token in tokens
            if POSITION_SYNONYMS.get(token, token) in available_positions
        }
        if eligible:
            return eligible

    stripped = normalized_slot.rstrip("1234567890")
    if stripped in SLOT_OVERRIDES:
        return SLOT_OVERRIDES[stripped]

    canonical = POSITION_SYNONYMS.get(stripped, stripped)
    if canonical in available_positions:
        return {canonical}

    # Fall back to all available positions when the slot type is unknown.
    return set(available_positions)

