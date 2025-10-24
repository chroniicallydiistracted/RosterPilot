"use client";

import useSWR from "swr";

import { UserLeaguesResponse } from "@/lib/api-types";

export function useUserLeagues() {
  return useSWR<UserLeaguesResponse, Error>("/me/leagues");
}
