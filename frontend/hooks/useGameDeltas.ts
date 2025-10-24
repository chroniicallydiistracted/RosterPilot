"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import { ErrorMessage, GameDelta, RuntimeConfig, WebSocketHandshake, WebSocketMessage } from "@/lib/api-types";
import { PublicEnv } from "@/lib/env";
import { buildWebSocketUrl } from "@/lib/url";

export type StreamMode = "live" | "replay";

export interface GameDeltaState {
  deltas: GameDelta[];
  handshake: WebSocketHandshake | null;
  lastHeartbeat: string | null;
  error: ErrorMessage | null;
  replayComplete: boolean;
  isConnected: boolean;
}

const INITIAL_STATE: GameDeltaState = {
  deltas: [],
  handshake: null,
  lastHeartbeat: null,
  error: null,
  replayComplete: false,
  isConnected: false
};

interface Options {
  mode: StreamMode;
  speed?: number;
}

function normalizePath(template: string, eventId: string): string {
  if (!template.includes("{event_id}")) {
    return template.endsWith(eventId) ? template : `${template.replace(/\/$/, "")}/${eventId}`;
  }
  return template.replace("{event_id}", encodeURIComponent(eventId));
}

export function useGameDeltas(
  env: PublicEnv,
  runtimeConfig: RuntimeConfig,
  eventId: string | null,
  options: Options
): GameDeltaState {
  const [state, setState] = useState<GameDeltaState>(INITIAL_STATE);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    setState(INITIAL_STATE);

    if (!eventId) {
      return undefined;
    }

    const template = runtimeConfig.websocket_paths?.game_updates ?? "/ws/games/{event_id}";
    const path = normalizePath(template, eventId);
    const url = buildWebSocketUrl(env.wsUrl, path);
    const params = new URLSearchParams({ mode: options.mode });
    if (options.mode === "replay" && options.speed) {
      params.set("speed", options.speed.toString());
    }
    const socketUrl = `${url}?${params.toString()}`;
    const socket = new WebSocket(socketUrl);
    wsRef.current = socket;

    socket.onopen = () => {
      setState((prev) => ({ ...prev, isConnected: true }));
    };

    socket.onclose = () => {
      setState((prev) => ({ ...prev, isConnected: false }));
    };

    socket.onerror = () => {
      setState((prev) => ({ ...prev, error: { type: "error", event_id: eventId, code: "socket_error", message: "WebSocket connection error" } }));
    };

    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data) as WebSocketMessage;
        handleMessage(payload);
      } catch (error) {
        console.error("Failed to parse websocket message", error);
      }
    };

    const handleMessage = (message: WebSocketMessage) => {
      if (message.type === "handshake") {
        setState((prev) => ({ ...prev, handshake: message }));
        return;
      }
      if (message.type === "heartbeat") {
        setState((prev) => ({ ...prev, lastHeartbeat: message.server_time }));
        return;
      }
      if (message.type === "error") {
        setState((prev) => ({ ...prev, error: message }));
        return;
      }
      if (message.type === "replay_complete") {
        setState((prev) => ({ ...prev, replayComplete: true }));
        return;
      }
      if (message.type === "delta") {
        setState((prev) => {
          const existing = new Map(prev.deltas.map((delta) => [delta.sequence, delta]));
          existing.set(message.data.sequence, message.data);
          const sorted = Array.from(existing.values()).sort((a, b) => a.sequence - b.sequence);
          return { ...prev, deltas: sorted };
        });
      }
    };

    return () => {
      socket.close();
      wsRef.current = null;
    };
  }, [env.wsUrl, eventId, options.mode, options.speed, runtimeConfig.websocket_paths?.game_updates]);

  return useMemo(() => state, [state]);
}
