export interface PlayerSnapshot {
  yahoo_player_id: string;
  full_name: string;
  team_abbr?: string | null;
  position: string;
  projected_points: number | null;
  actual_points: number | null;
  status?: string | null;
}

export interface RosterEntry {
  slot: string;
  player: PlayerSnapshot;
  recommended: boolean;
  locked: boolean;
}

export interface OptimizerSummary {
  recommended_starters: string[];
  delta_points: number | null;
  rationale: string[];
  source?: string | null;
}

export interface LeagueTeamSummary {
  team_key: string;
  name: string;
  manager: string;
}

export interface LeagueSummary {
  league_key: string;
  name: string;
  season: number;
  avatar_url?: string | null;
  status?: string | null;
}

export interface UserLeaguesResponse {
  leagues: LeagueSummary[];
  generated_at: string;
}

export interface LeagueRosterResponse {
  league_key: string;
  week: number;
  team: LeagueTeamSummary;
  generated_at: string;
  starters: RosterEntry[];
  bench: RosterEntry[];
  optimizer?: OptimizerSummary | null;
}

export type RosterSlot = RosterEntry;

export interface LiveTeamSnapshot {
  abbr: string;
  score: number;
}

export interface LiveGameSummary {
  event_id: string;
  home: LiveTeamSnapshot;
  away: LiveTeamSnapshot;
  venue: { name: string };
  status: string;
  quarter: number | null;
  clock: string | null;
}

export interface LiveGamesResponse {
  games: LiveGameSummary[];
  generated_at: string;
}

export interface PlaySummary {
  play_id: string;
  quarter: number;
  clock: string;
  description: string;
}

export interface DriveSummary {
  drive_id: string;
  team: { abbr: string };
  result: string;
  start_clock: string;
  end_clock: string;
  plays: PlaySummary[];
}

export interface PlayByPlayResponse {
  event_id: string;
  drives: DriveSummary[];
  generated_at: string;
}

export interface FeatureFlags {
  replay: boolean;
  [key: string]: boolean | undefined;
}

export interface WebSocketPaths {
  game_updates: string;
  [key: string]: string | undefined;
}

export interface RuntimeConfig {
  api_base_url: string;
  websocket_paths: WebSocketPaths;
  feature_flags: FeatureFlags;
  version?: string;
  generated_at?: string;
}

export interface GameDelta {
  sequence: number;
  type: string;
  description?: string | null;
  quarter?: number | null;
  clock?: string | null;
  flags: string[];
}

export interface WebSocketHandshake {
  type: "handshake";
  event_id: string;
  heartbeat_sec: number;
}

export interface HeartbeatMessage {
  type: "heartbeat";
  event_id: string;
  server_time: string;
}

export interface ReplayCompleteMessage {
  type: "replay_complete";
  event_id: string;
}

export interface ErrorMessage {
  type: "error";
  event_id: string;
  code: string;
  message?: string | null;
}

export interface GameDeltaEnvelope {
  type: "delta";
  event_id: string;
  data: GameDelta;
}

export type WebSocketMessage =
  | WebSocketHandshake
  | HeartbeatMessage
  | ReplayCompleteMessage
  | ErrorMessage
  | GameDeltaEnvelope;
