"use client";

import useSWR from "swr";

import { LiveGamesResponse } from "@/lib/api-types";

export function useLiveGames() {
  return useSWR<LiveGamesResponse, Error>("/games/live", { refreshInterval: 60_000 });
}
