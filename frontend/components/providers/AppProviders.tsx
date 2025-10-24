"use client";

import { ReactNode, createContext, useContext, useEffect, useMemo, useState } from "react";
import { SWRConfig } from "swr";

import { LeagueSummary, RuntimeConfig } from "@/lib/api-types";
import { createApiFetcher } from "@/lib/api-client";
import { PublicEnv } from "@/lib/env";
import { useUserLeagues } from "@/hooks/useUserLeagues";

interface AppProvidersProps {
  children: ReactNode;
  env: PublicEnv;
  runtimeConfig: RuntimeConfig;
}

const EnvContext = createContext<PublicEnv | null>(null);
const RuntimeConfigContext = createContext<RuntimeConfig | null>(null);

export interface LeagueContextValue {
  leagues: LeagueSummary[];
  selectedLeagueKey: string | null;
  setSelectedLeagueKey: (leagueKey: string | null) => void;
  week: number;
  setWeek: (week: number) => void;
  isLoading: boolean;
  error: Error | undefined;
  lastUpdated: string | null;
}

const LeagueContext = createContext<LeagueContextValue | null>(null);

function LeagueProvider({ children }: { children: ReactNode }) {
  const { data, error, isLoading } = useUserLeagues();
  const [selectedLeagueKey, setSelectedLeagueKey] = useState<string | null>(null);
  const [week, setWeek] = useState<number>(1);

  useEffect(() => {
    if (!selectedLeagueKey && data?.leagues?.length) {
      setSelectedLeagueKey(data.leagues[0].league_key);
    }
  }, [data, selectedLeagueKey]);

  const value = useMemo<LeagueContextValue>(() => ({
    leagues: data?.leagues ?? [],
    selectedLeagueKey,
    setSelectedLeagueKey: (key: string | null) => setSelectedLeagueKey(key),
    week,
    setWeek,
    isLoading,
    error,
    lastUpdated: data?.generated_at ?? null
  }), [data, error, isLoading, selectedLeagueKey, week]);

  return <LeagueContext.Provider value={value}>{children}</LeagueContext.Provider>;
}

export function AppProviders({ children, env, runtimeConfig }: AppProvidersProps) {
  const fetcher = useMemo(() => createApiFetcher(env, runtimeConfig), [env, runtimeConfig]);

  return (
    <SWRConfig value={{ fetcher, revalidateOnFocus: false, revalidateOnReconnect: true }}>
      <EnvContext.Provider value={env}>
        <RuntimeConfigContext.Provider value={runtimeConfig}>
          <LeagueProvider>{children}</LeagueProvider>
        </RuntimeConfigContext.Provider>
      </EnvContext.Provider>
    </SWRConfig>
  );
}

export function useEnv(): PublicEnv {
  const ctx = useContext(EnvContext);
  if (!ctx) {
    throw new Error("useEnv must be used within AppProviders");
  }
  return ctx;
}

export function useRuntimeConfig(): RuntimeConfig {
  const ctx = useContext(RuntimeConfigContext);
  if (!ctx) {
    throw new Error("useRuntimeConfig must be used within AppProviders");
  }
  return ctx;
}

export function useLeagueContext(): LeagueContextValue {
  const ctx = useContext(LeagueContext);
  if (!ctx) {
    throw new Error("useLeagueContext must be used within AppProviders");
  }
  return ctx;
}
