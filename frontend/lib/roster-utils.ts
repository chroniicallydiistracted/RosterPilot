import type { LeagueRosterResponse, RosterEntry } from "@/lib/api-types";

export interface LineupSuggestion {
  from: RosterEntry;
  to: RosterEntry;
  delta: number;
}

const toPoints = (value: number | null | undefined): number =>
  typeof value === "number" ? value : 0;

export const formatPoints = (value: number | null | undefined): string => {
  if (value === null || value === undefined) {
    return "-";
  }
  return value.toFixed(1);
};

export const buildLineupSuggestions = (roster: LeagueRosterResponse): LineupSuggestion[] => {
  const optimizer = roster.optimizer;
  if (!optimizer || optimizer.recommended_starters.length === 0) {
    return [];
  }

  const recommended = new Set(optimizer.recommended_starters.map((name) => name.toLowerCase()));
  const starters = roster.starters.map((entry) => ({
    entry,
    key: entry.player.full_name.toLowerCase(),
  }));

  const suggestions: LineupSuggestion[] = [];

  for (const benchEntry of roster.bench) {
    const benchKey = benchEntry.player.full_name.toLowerCase();
    if (!recommended.has(benchKey)) {
      continue;
    }

    const target = starters.find(({ entry }) => {
      if (recommended.has(entry.player.full_name.toLowerCase())) {
        return false;
      }
      if (benchEntry.slot === "BENCH") {
        return true;
      }
      return entry.slot === benchEntry.slot;
    });

    if (!target) {
      continue;
    }

    const delta = toPoints(benchEntry.player.projected_points) - toPoints(target.entry.player.projected_points);
    suggestions.push({ from: target.entry, to: benchEntry, delta });
  }

  return suggestions.sort((a, b) => b.delta - a.delta);
};
