"use client";

import useSWR from "swr";

import { LeagueRosterResponse } from "@/lib/api-types";

export function useLeagueRoster(leagueKey: string | null, week: number) {
  const shouldFetch = Boolean(leagueKey);
  const encodedKey = leagueKey ? encodeURIComponent(leagueKey) : "";
  const path = shouldFetch ? `/leagues/${encodedKey}/roster?week=${week}` : null;
  return useSWR<LeagueRosterResponse, Error>(path);
}
