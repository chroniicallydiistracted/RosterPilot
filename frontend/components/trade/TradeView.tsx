"use client";

import { EmptyState } from "@/components/common/EmptyState";
import { ProvenanceBadge } from "@/components/common/ProvenanceBadge";
import { useLeagueContext } from "@/components/providers/AppProviders";

import styles from "./TradeView.module.css";

export function TradeView() {
  const { selectedLeagueKey, leagues } = useLeagueContext();

  if (!selectedLeagueKey) {
    return (
      <EmptyState
        title="Select a league to evaluate trades"
        description="Pick a league to compare proposed trades, analyze positional balance, and summarize long-term impact."
      />
    );
  }

  const league = leagues.find((item) => item.league_key === selectedLeagueKey);

  return (
    <section className={styles.layout} aria-label="Trade evaluator roadmap">
      <article className={styles.card}>
        <div className={styles.header}>
          <h2 className={styles.title}>Trade Evaluator (in progress)</h2>
          <div className={styles.badgeRow}>
            <ProvenanceBadge source="yahoo" />
            <ProvenanceBadge source="pyespn" />
            <ProvenanceBadge source="optimizer" label="VORP" />
          </div>
        </div>
        <p className={styles.description}>
          The trade workspace will balance value over replacement, playoff schedule difficulty, and positional depth for
          <strong> {league?.name ?? selectedLeagueKey}</strong>. It keeps you firmly in read-only territory—generating human-friendly
          advisories you can apply manually in Yahoo.
        </p>
        <div className={styles.gridColumns}>
          <div>
            <h3 className={styles.sectionTitle}>My Team</h3>
            <div className={styles.placeholderField}>Lineup picker and lock controls (coming soon)</div>
          </div>
          <div>
            <h3 className={styles.sectionTitle}>Trade Partner</h3>
            <div className={styles.placeholderField}>Roster selector with depth/bye insights (coming soon)</div>
          </div>
          <div>
            <h3 className={styles.sectionTitle}>Impact Summary</h3>
            <div className={styles.placeholderField}>Delta chart and fairness meter (coming soon)</div>
          </div>
        </div>
      </article>

      <article className={styles.card} aria-label="Upcoming trade rationale">
        <h2 className={styles.title}>What you’ll see next</h2>
        <ul className={styles.rationaleList}>
          <li>Net projected points over the next 4 weeks and fantasy playoffs.</li>
          <li>Schedule strength overlays sourced from PyESPN venues and events data.</li>
          <li>Risk flags for injury designations, bye clusters, and workload volatility.</li>
        </ul>
      </article>
    </section>
  );
}
