"use client";

import clsx from "clsx";
import { useEffect, useState } from "react";

import { EmptyState } from "@/components/common/EmptyState";
import { LoadingState } from "@/components/common/LoadingState";
import { ProvenanceBadge } from "@/components/common/ProvenanceBadge";
import { useEnv, useRuntimeConfig } from "@/components/providers/AppProviders";
import { useGameDeltas, StreamMode } from "@/hooks/useGameDeltas";
import { useLiveGames } from "@/hooks/useLiveGames";
import { usePlayByPlay } from "@/hooks/usePlayByPlay";

import styles from "./LiveGameCenterView.module.css";

export function LiveGameCenterView() {
  const env = useEnv();
  const runtimeConfig = useRuntimeConfig();
  const { data: liveData, error: liveError, isLoading: liveLoading } = useLiveGames();
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);
  const [mode, setMode] = useState<StreamMode>("live");
  const [speed, setSpeed] = useState<number>(1);

  useEffect(() => {
    if (!selectedEventId && liveData?.games?.length) {
      setSelectedEventId(liveData.games[0].event_id);
    }
  }, [liveData, selectedEventId]);

  useEffect(() => {
    if (!runtimeConfig.feature_flags.replay && mode === "replay") {
      setMode("live");
    }
  }, [mode, runtimeConfig.feature_flags.replay]);

  const { data: pbpData, isLoading: pbpLoading } = usePlayByPlay(selectedEventId);
  const deltaState = useGameDeltas(env, runtimeConfig, selectedEventId, { mode, speed });

  if (liveError) {
    return (
      <EmptyState
        title="Live games unavailable"
        description="Unable to load live game metadata from the backend. Confirm PyESPN ingestion is running and retry."
      />
    );
  }

  if (liveLoading || !liveData) {
    return <LoadingState label="Fetching live games" />;
  }

  if (!liveData.games.length) {
    return (
      <EmptyState
        title="No tracked games"
        description="Ingestion hasn't loaded NFL events yet. Once PyESPN fixtures sync, live games and replays will appear here."
      />
    );
  }

  return (
    <div className={styles.layout}>
      <section className={styles.card} aria-label="Tracked games">
        <div className={styles.header}>
          <h2 className={styles.title}>Live scoreboard</h2>
          <ProvenanceBadge source="pyespn" />
        </div>
        <div className={styles.gameList}>
          {liveData.games.map((game) => {
            const isActive = selectedEventId === game.event_id;
            return (
              <button
                key={game.event_id}
                type="button"
                onClick={() => setSelectedEventId(game.event_id)}
                className={clsx(styles.gameButton, isActive && styles.gameButtonActive)}
                aria-pressed={isActive}
              >
                <div className={styles.scoreRow}>
                  <span>
                    {game.away.abbr} {game.away.score}
                  </span>
                  <span>
                    {game.home.abbr} {game.home.score}
                  </span>
                </div>
                <div className={styles.metaRow}>
                  <span>
                    {game.status} {game.quarter ? `Q${game.quarter}` : ""} {game.clock ?? ""}
                  </span>
                  <span>{game.venue.name}</span>
                </div>
              </button>
            );
          })}
        </div>
      </section>

      <div className={styles.content}>
        <section className={styles.card} aria-label="Live delta feed">
          <div className={styles.header}>
            <h2 className={styles.title}>Live feed</h2>
            <ProvenanceBadge source="pyespn" />
          </div>
          <div className={styles.controls}>
            <button
              type="button"
              onClick={() => setMode("live")}
              className={clsx(styles.modeToggle, mode === "live" && styles.modeToggleActive)}
            >
              Live
            </button>
            <button
              type="button"
              onClick={() => runtimeConfig.feature_flags.replay && setMode("replay")}
              className={clsx(styles.modeToggle, mode === "replay" && styles.modeToggleActive)}
              disabled={!runtimeConfig.feature_flags.replay}
            >
              Replay
            </button>
            {mode === "replay" ? (
              <label className={styles.speedControl}>
                Speed
                <input
                  type="range"
                  min={0.5}
                  max={4}
                  step={0.5}
                  value={speed}
                  onChange={(event) => setSpeed(Number(event.target.value))}
                  aria-label="Replay speed"
                />
                {speed.toFixed(1)}x
              </label>
            ) : null}
          </div>

          {deltaState.error ? (
            <EmptyState
              title="Stream error"
              description={deltaState.error.message || "The realtime stream returned an error payload."}
            />
          ) : (
            <div className={styles.playList}>
              {deltaState.deltas.map((delta) => (
                <article key={delta.sequence} className={styles.playItem}>
                  <div className={styles.playHeader}>
                    <span>
                      {delta.quarter ? `Q${delta.quarter}` : "--"} · {delta.clock ?? "0:00"}
                    </span>
                    <span>{delta.type}</span>
                  </div>
                  {delta.description ? <p className={styles.playDescription}>{delta.description}</p> : null}
                  {delta.flags.length ? (
                    <div className={styles.flagRow}>
                      {delta.flags.map((flag) => (
                        <span key={flag} className={styles.flag}>
                          {flag}
                        </span>
                      ))}
                    </div>
                  ) : null}
                </article>
              ))}
            </div>
          )}

          <div className={styles.statusBar}>
            <span>
              {deltaState.handshake ? `Heartbeat ${deltaState.handshake.heartbeat_sec}s` : "Awaiting handshake"}
            </span>
            <span>
              {deltaState.replayComplete ? "Replay finished" : `Deltas: ${deltaState.deltas.length}`} ·
              {deltaState.isConnected ? " Connected" : " Disconnected"}
            </span>
          </div>
        </section>

        <section className={styles.card} aria-label="Drive timeline">
          <div className={styles.header}>
            <h2 className={styles.title}>Drive timeline</h2>
            <ProvenanceBadge source="pyespn" />
          </div>
          {pbpLoading || !pbpData ? (
            <LoadingState label="Loading play-by-play" />
          ) : (
            <div className={styles.timeline}>
              {pbpData.drives.map((drive) => (
                <article key={drive.drive_id} className={styles.driveItem}>
                  <div className={styles.driveHeader}>
                    <span>
                      {drive.team.abbr} • {drive.result}
                    </span>
                    <span>
                      {drive.start_clock} → {drive.end_clock}
                    </span>
                  </div>
                  <ul className={styles.rationaleList}>
                    {drive.plays.map((play) => (
                      <li key={play.play_id}>
                        Q{play.quarter} {play.clock} · {play.description}
                      </li>
                    ))}
                  </ul>
                </article>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
