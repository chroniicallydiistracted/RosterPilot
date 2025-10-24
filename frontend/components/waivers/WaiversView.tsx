"use client";

import { EmptyState } from "@/components/common/EmptyState";
import { ProvenanceBadge } from "@/components/common/ProvenanceBadge";
import { useLeagueContext } from "@/components/providers/AppProviders";

import styles from "./WaiversView.module.css";

export function WaiversView() {
  const { selectedLeagueKey, leagues } = useLeagueContext();

  if (!selectedLeagueKey) {
    return (
      <EmptyState
        title="Select a league to explore waivers"
        description="Choose a Yahoo league to evaluate free agents and projection-driven bidding guidance."
      />
    );
  }

  const league = leagues.find((item) => item.league_key === selectedLeagueKey);

  return (
    <section className={styles.card} aria-label="Waiver board">
      <div className={styles.header}>
        <h2 className={styles.title}>Advisory Waiver Board</h2>
        <span className={styles.betaBadge}>Roadmap</span>
      </div>
      <p className={styles.description}>
        We’re preparing a data-backed waiver surface for <strong>{league?.name ?? selectedLeagueKey}</strong>. It will blend Yahoo
        projections with roster gaps, bye weeks, and PyESPN schedule difficulty to recommend FAAB ranges and roster fits.
      </p>
      <ul className={styles.highlightList}>
        <li>
          Rank free agents by projected value over replacement with provenance badges for Yahoo (fantasy context) and PyESPN (NFL
          schedule insights).
        </li>
        <li>Surface injury and bye-week alerts so you can act before waiver deadlines close.</li>
        <li>Export shortlists or share a permalink with co-managers—no automated Yahoo actions to stay within read-only scope.</li>
      </ul>
      <p className={styles.description}>
        This view will activate once <ProvenanceBadge source="yahoo" /> and <ProvenanceBadge source="pyespn" /> datasets expose the
        free-agent pool. Keep an eye on the changelog as Phase 3+ endpoints land.
      </p>
    </section>
  );
}
