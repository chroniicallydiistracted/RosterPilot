"use client";

import clsx from "clsx";
import Link from "next/link";
import { usePathname } from "next/navigation";
import type { Route } from "next";
import { ReactNode, useMemo } from "react";

import { useLeagueContext, useEnv } from "@/components/providers/AppProviders";
import styles from "./AppShell.module.css";

interface AppShellProps {
  children: ReactNode;
}

const NAV_ITEMS: Array<{ href: Route; label: string }> = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/optimizer", label: "Optimizer" },
  { href: "/waivers", label: "Waivers" },
  { href: "/trade", label: "Trade Evaluator" },
  { href: "/live", label: "Live Game Center" }
];

function formatSyncedTimestamp(timestamp: string | null): string {
  if (!timestamp) {
    return "Waiting for sync";
  }
  const date = new Date(timestamp);
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: true
  }).format(date);
}

export function AppShell({ children }: AppShellProps) {
  const pathname = usePathname();
  const { environment } = useEnv();
  const { leagues, selectedLeagueKey, setSelectedLeagueKey, week, setWeek, isLoading, lastUpdated } = useLeagueContext();

  const leagueOptions = useMemo(() => leagues.map((league) => ({
    key: league.league_key,
    label: `${league.name} · ${league.season}`
  })), [leagues]);

  return (
    <div className={styles.appShell}>
      <a className={styles.skipLink} href="#main-content">
        Skip to content
      </a>
      <aside className={styles.sidebar} aria-label="Main navigation">
        <h1 className={styles.brand}>RosterPilot</h1>
        <div className={styles.environmentBadge} aria-live="polite">
          {environment}
        </div>
        <nav>
          <ul className={styles.navList}>
            {NAV_ITEMS.map((item) => (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={clsx(styles.navLink, pathname.startsWith(item.href) && styles.navLinkActive)}
                >
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      </aside>
      <div className={styles.mainPane}>
        <header className={styles.header}>
          <div className={styles.headerLeft}>
            <span className={styles.lastSynced}>Last synced: {formatSyncedTimestamp(lastUpdated)}</span>
          </div>
          <div className={styles.controls}>
            <label className={styles.selectGroup}>
              <span className={styles.selectLabel}>League</span>
              <select
                className={styles.selectField}
                value={selectedLeagueKey ?? ""}
                onChange={(event) => setSelectedLeagueKey(event.target.value || null)}
                disabled={isLoading || leagueOptions.length === 0}
                aria-label="Select fantasy league"
              >
                <option value="" disabled>
                  {isLoading ? "Loading leagues…" : "Select a league"}
                </option>
                {leagueOptions.map((league) => (
                  <option key={league.key} value={league.key}>
                    {league.label}
                  </option>
                ))}
              </select>
            </label>
            <label className={styles.selectGroup}>
              <span className={styles.selectLabel}>Week</span>
              <select
                className={styles.selectField}
                value={week}
                onChange={(event) => setWeek(Number(event.target.value))}
                aria-label="Select scoring week"
              >
                {Array.from({ length: 18 }, (_, index) => index + 1).map((value) => (
                  <option key={value} value={value}>
                    Week {value}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </header>
        <main id="main-content" className={styles.mainContent}>
          {children}
        </main>
      </div>
    </div>
  );
}
