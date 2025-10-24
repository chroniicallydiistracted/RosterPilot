"use client";

import useSWR from "swr";

import { PlayByPlayResponse } from "@/lib/api-types";

export function usePlayByPlay(eventId: string | null) {
  const encoded = eventId ? encodeURIComponent(eventId) : "";
  const path = eventId ? `/games/${encoded}/pbp` : null;
  return useSWR<PlayByPlayResponse, Error>(path, { refreshInterval: 120_000 });
}
