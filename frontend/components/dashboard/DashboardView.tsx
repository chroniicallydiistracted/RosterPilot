"use client";

import { useMemo } from "react";

import { EmptyState } from "@/components/common/EmptyState";
import { LoadingState } from "@/components/common/LoadingState";
import { ProvenanceBadge } from "@/components/common/ProvenanceBadge";
import { useLeagueContext } from "@/components/providers/AppProviders";
import { useLeagueRoster } from "@/hooks/useLeagueRoster";
import { formatPoints } from "@/lib/roster-utils";
import { RosterSlot } from "@/lib/api-types";

import styles from "./DashboardView.module.css";

function RosterTable({
  title,
  slots,
  source
}: {
  title: string;
  slots: RosterSlot[];
  source: "yahoo" | "pyespn";
}) {
  return (
    <section className={styles.card} aria-label={title}>
      <div className={styles.cardHeader}>
        <h2 className={styles.cardTitle}>{title}</h2>
        <ProvenanceBadge source={source} />
      </div>
      <div className={styles.tableWrapper}>
        <table>
          <thead>
            <tr>
              <th scope="col">Slot</th>
              <th scope="col">Player</th>
              <th scope="col">Team</th>
              <th scope="col">Proj</th>
              <th scope="col">Actual</th>
              <th scope="col">Status</th>
            </tr>
          </thead>
          <tbody>
            {slots.map((slot) => (
              <tr key={`${slot.slot}-${slot.player.yahoo_player_id}`} className={slot.recommended ? styles.recommended : undefined}>
                <td className={styles.slotCell}>{slot.slot}</td>
                <td className={styles.playerName}>{slot.player.full_name}</td>
                <td>{slot.player.team_abbr}</td>
                <td>{formatPoints(slot.player.projected_points)}</td>
                <td>{formatPoints(slot.player.actual_points ?? null)}</td>
                <td>{slot.player.status ?? ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export function DashboardView() {
  const { selectedLeagueKey, week, leagues } = useLeagueContext();
  const { data, error, isLoading } = useLeagueRoster(selectedLeagueKey, week);

  const leagueName = useMemo(() => leagues.find((league) => league.league_key === selectedLeagueKey)?.name ?? "", [
    leagues,
    selectedLeagueKey
  ]);

  if (!selectedLeagueKey) {
    return (
      <EmptyState
        title="Select a league to begin"
        description="Choose a Yahoo Fantasy league to review lineup health, projections, and optimizer guidance."
      />
    );
  }

  if (error) {
    return (
      <EmptyState
        title="Roster data unavailable"
        description="We couldn't fetch lineup data from the API. Please retry in a moment and confirm your backend service is reachable."
      />
    );
  }

  if (!data || isLoading) {
    return <LoadingState label="Fetching roster" />;
  }

  const { team, starters, bench, optimizer, generated_at } = data;

  return (
    <div className={styles.layout}>
      <section className={styles.card} aria-label="Team summary">
        <div className={styles.cardHeader}>
          <h2 className={styles.cardTitle}>{team.name}</h2>
          <div className={styles.badgeRow}>
            <ProvenanceBadge source="yahoo" />
          </div>
        </div>
        <p className={styles.cardDescription}>
          {team.manager} manages the roster for <strong>{leagueName || team.team_key}</strong>.
          Track projected vs. actual output to stay ahead of lineup lock.
        </p>
        <p className={styles.muted}>Generated {new Date(generated_at).toLocaleString()}</p>
      </section>

      <div className={styles.gridTwo}>
        <RosterTable title="Starters" slots={starters} source="yahoo" />
        <RosterTable title="Bench" slots={bench} source="yahoo" />
      </div>

      {optimizer ? (
        <section className={styles.card} aria-label="Optimizer insights">
          <div className={styles.cardHeader}>
            <h2 className={styles.cardTitle}>Optimizer highlights</h2>
            <ProvenanceBadge source="optimizer" />
          </div>
          <p className={styles.cardDescription}>
            Recommended lineup projects {optimizer.delta_points?.toFixed(1) ?? "0.0"} more points than the current starters.
          </p>
          <ul className={styles.optimizerDetails}>
            {optimizer.rationale.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </section>
      ) : null}
    </div>
  );
}
