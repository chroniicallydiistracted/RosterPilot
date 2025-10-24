import type { PublicEnv } from "@/lib/env";
import type { RuntimeConfig } from "@/lib/api-types";

const sanitizePath = (path: string): string => (path.startsWith("/") ? path : `/${path}`);

function buildApiUrl(env: PublicEnv, path: string): string {
  const base = new URL(env.apiUrl);
  base.pathname = `${base.pathname.replace(/\/+$/, "")}${sanitizePath(path)}`;
  return base.toString();
}

async function parseJson<T>(response: Response): Promise<T> {
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export function createApiFetcher(_env: PublicEnv, runtimeConfig: RuntimeConfig) {
  return async <T>(path: string, init?: RequestInit): Promise<T> => {
    const url = new URL(runtimeConfig.api_base_url ?? _env.apiUrl);
    url.pathname = `${url.pathname.replace(/\/+$/, "")}${sanitizePath(path)}`;
    const response = await fetch(url.toString(), {
      ...init,
      headers: {
        Accept: "application/json",
        ...(init?.headers ?? {}),
      },
    });

    if (!response.ok) {
      throw new Error(`Request to ${url.toString()} failed with status ${response.status}`);
    }

    return parseJson<T>(response);
  };
}

export async function fetchRuntimeConfig(env: PublicEnv): Promise<RuntimeConfig> {
  let payload: RuntimeConfig | undefined;
  try {
    const response = await fetch(buildApiUrl(env, "/runtime/config"), {
      headers: { Accept: "application/json" },
      next: { revalidate: 60 },
    });

    if (response.ok) {
      payload = await parseJson<RuntimeConfig>(response);
    }
  } catch (error) {
    console.warn("Failed to load runtime config, falling back to defaults", error);
  }

  if (!payload) {
    return {
      api_base_url: env.apiUrl,
      websocket_paths: { game_updates: "/ws/games/{event_id}" },
      feature_flags: { replay: false },
    };
  }

  const websocketPaths = { ...(payload.websocket_paths ?? {}) };
  if (!websocketPaths.game_updates) {
    websocketPaths.game_updates = "/ws/games/{event_id}";
  }

  const featureFlags = { ...(payload.feature_flags ?? {}) };
  if (featureFlags.replay === undefined) {
    featureFlags.replay = false;
  }

  return {
    api_base_url: payload.api_base_url ?? env.apiUrl,
    websocket_paths: websocketPaths,
    feature_flags: featureFlags,
    version: payload.version,
    generated_at: payload.generated_at,
  };
}
