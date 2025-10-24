"use client";

import { useMemo, useState } from "react";

import { EmptyState } from "@/components/common/EmptyState";
import { LoadingState } from "@/components/common/LoadingState";
import { ProvenanceBadge } from "@/components/common/ProvenanceBadge";
import { useLeagueContext } from "@/components/providers/AppProviders";
import { useLeagueRoster } from "@/hooks/useLeagueRoster";
import { LineupSuggestion, buildLineupSuggestions, formatPoints } from "@/lib/roster-utils";

import styles from "./OptimizerView.module.css";

export function OptimizerView() {
  const { selectedLeagueKey, week } = useLeagueContext();
  const { data, error, isLoading } = useLeagueRoster(selectedLeagueKey, week);
  const [lockedPlayers, setLockedPlayers] = useState<Record<string, boolean>>({});

  const suggestions: LineupSuggestion[] = useMemo(() => (data ? buildLineupSuggestions(data) : []), [data]);
  const optimizer = data?.optimizer ?? null;

  const recommendedSet = useMemo(() => {
    if (!data?.optimizer?.recommended_starters?.length) {
      return new Set<string>();
    }
    return new Set(data.optimizer.recommended_starters.map((name) => name.toLowerCase()));
  }, [data?.optimizer?.recommended_starters]);

  const recommendedLineup = useMemo(() => {
    if (!data) {
      return [];
    }
    return data.starters.map((slot) => ({
      slot: slot.slot,
      player: slot.player,
      recommended: slot.recommended || recommendedSet.has(slot.player.full_name.toLowerCase())
    }));
  }, [data, recommendedSet]);

  if (!selectedLeagueKey) {
    return (
      <EmptyState
        title="Optimizer requires a league"
        description="Select a league to compare your current lineup to the solver's recommendation."
      />
    );
  }

  if (error) {
    return (
      <EmptyState
        title="Unable to load optimizer data"
        description="The optimizer response was not available. Ensure backend contract tests pass and retry."
      />
    );
  }

  if (!data || isLoading) {
    return <LoadingState label="Running optimizer" />;
  }

  const toggleLock = (playerId: string) => {
    setLockedPlayers((prev) => ({ ...prev, [playerId]: !prev[playerId] }));
  };

  return (
    <div className={styles.layout}>
      <section className={styles.card} aria-label="Optimizer summary">
        <div className={styles.header}>
          <h2 className={styles.title}>Projected gain</h2>
          <div className={styles.badgeRow}>
            <ProvenanceBadge source="optimizer" />
          </div>
        </div>
        <p className={styles.description}>
          {optimizer ? (
            <>Switching to the recommended lineup yields <strong>+{(optimizer.delta_points ?? 0).toFixed(1)} points</strong> based on
            current Yahoo projections. Lock any players you want to keep anchored before requesting a recompute.</>
          ) : (
            "Optimizer results are not available yet. Keep playing games to unlock solver insights."
          )}
        </p>
        {suggestions.length === 0 ? (
          <p className={styles.emptyCopy}>Your current starters already align with the optimizer’s recommendation.</p>
        ) : (
          <div className={styles.suggestions}>
            {suggestions.map((suggestion) => {
              const benchPlayer = suggestion.to.player;
              const locked = lockedPlayers[benchPlayer.yahoo_player_id] ?? false;
              return (
                <article key={`${suggestion.from.player.yahoo_player_id}-${benchPlayer.yahoo_player_id}`} className={styles.suggestion}>
                  <div className={styles.suggestionHeader}>
                    <span>
                      Start {benchPlayer.full_name} over {suggestion.from.player.full_name}
                    </span>
                    <span className={styles.deltaPositive}>+{suggestion.delta.toFixed(1)} pts</span>
                  </div>
                  <p className={styles.playerMeta}>
                    {benchPlayer.position} · {benchPlayer.team_abbr} — {formatPoints(benchPlayer.projected_points)} projected
                    points.
                  </p>
                  <div className={styles.lockControls}>
                    <label className={styles.lockLabel}>
                      <input
                        type="checkbox"
                        className={styles.lockToggle}
                        checked={locked}
                        onChange={() => toggleLock(benchPlayer.yahoo_player_id)}
                        aria-label={`Lock ${benchPlayer.full_name}`}
                      />
                      Lock this player in future solves
                    </label>
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </section>

      <section className={styles.card} aria-label="Recommended lineup">
        <div className={styles.header}>
          <h2 className={styles.title}>Recommended starters</h2>
          <ProvenanceBadge source="optimizer" />
        </div>
        <div className={styles.tableWrapper}>
          <table>
            <thead>
              <tr>
                <th scope="col">Slot</th>
                <th scope="col">Player</th>
                <th scope="col">Team</th>
                <th scope="col">Proj</th>
                <th scope="col">Status</th>
                <th scope="col">Locked</th>
              </tr>
            </thead>
            <tbody>
              {recommendedLineup.map((entry) => {
                const locked = lockedPlayers[entry.player.yahoo_player_id] ?? false;
                return (
                  <tr key={`${entry.slot}-${entry.player.yahoo_player_id}`}>
                    <td>{entry.slot}</td>
                    <td>{entry.player.full_name}</td>
                    <td>{entry.player.team_abbr}</td>
                    <td>{formatPoints(entry.player.projected_points)}</td>
                    <td>{entry.player.status ?? ""}</td>
                    <td>{locked ? "Locked" : "Unlocked"}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
