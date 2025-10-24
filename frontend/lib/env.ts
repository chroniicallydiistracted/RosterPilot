export interface PublicEnv {
  apiUrl: string;
  wsUrl: string;
  appEnv: string;
  environment: string;
}

const trimTrailingSlash = (value: string): string => value.replace(/\/+$/, "");

export function readPublicEnv(): PublicEnv {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";
  const wsUrl = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/ws";
  const appEnv = process.env.NEXT_PUBLIC_ENV ?? "development";

  return {
    apiUrl: trimTrailingSlash(apiUrl),
    wsUrl: trimTrailingSlash(wsUrl),
    appEnv,
    environment: appEnv,
  };
}

export function createPublicEnv(overrides: Partial<PublicEnv> = {}): PublicEnv {
  const base = readPublicEnv();
  const merged = { ...base, ...overrides };
  return {
    ...merged,
    environment: merged.environment ?? merged.appEnv,
  };
}
