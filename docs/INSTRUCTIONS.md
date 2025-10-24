# Yahoo + PyESPN Fantasy Companion — Build Instructions (Read‑Only Yahoo)

**Date:** 2025-10-23  
**Scope:** Read‑only Yahoo Fantasy Sports API. PyESPN for official NFL (schedules, teams, rosters, events, drives, plays, logos, venues). Weather instructions deferred; you confirmed weather fields are embedded in the stadium/matchup JSON and will supply a separate guide later.

## 1) Objectives
- Optimize a logged‑in Yahoo user’s fantasy team with analysis and guidance. No write actions.  
- Render live, broadcast‑style scoreboard and animated play diagrams for NFL games from PyESPN event/drives/plays.  
- Keep data provenance strict: Fantasy context from Yahoo; Official NFL context from PyESPN.

## 2) Architecture
- **Frontend:** Next.js/React + TypeScript. Canvas (PixiJS) for field + animations. WebSocket client for deltas.  
- **Backend:** FastAPI (Python 3.11+). Ingestion jobs for Yahoo and PyESPN. Redis for cache/pubsub. Postgres for durable state.  
- **Realtime:** WS hub broadcasting compact game deltas derived from PyESPN.  
- **Observability:** Structured logs, tracing, error reporting.

## 3) Authentication and permissions
- Yahoo OAuth2 Authorization Code flow. Scope: `fspt-r` only. Store refresh tokens securely. Handle token refresh and revocation.  
- No Yahoo write scope. App functions as a companion/advisor; user commits changes in the Yahoo app.

## 4) Data contracts
- **Yahoo (fantasy-only):** user→games→leagues→teams→rosters→players, standings, projections/actuals, waivers, transactions. Request JSON with `format=json` where available.  
- **PyESPN (official NFL):** season schedule, events, teams, images/logos, venues, drives, plays. Treat schemas as unofficial and subject to change. Implement guards and caching.  
- **Weather:** deferred. Use the embedded stadium/matchup JSON fields when you publish the separate weather guide.

## 5) Minimal persistent model (Postgres)
- `users(user_id, yahoo_sub, created_at)`  
- `oauth_tokens(user_id, provider, access_token, refresh_token, expires_at, scopes)`  
- `yahoo_leagues(league_key, user_id, season, name, scoring_json)`  
- `yahoo_teams(team_key, league_key, name, manager)`  
- `yahoo_rosters(team_key, week, slot, yahoo_player_id)`  
- `yahoo_players(yahoo_player_id, name, pos, team_abbr, status, bye_week)`  
- `events(event_id, season, week, start_ts, status, home_id, away_id, venue_id)`  
- `teams(espn_team_id, name, abbr, colors_json, logos_json)`  
- `venues(venue_id, name, city, roof_type, surface, lat, lon)`  
- `drives(event_id, drive_id, start_yardline_100, end_yardline_100, result, start_clock, end_clock)`  
- `plays(event_id, play_id, drive_id, sequence, clock, quarter, down, distance, yardline_100, type, yards, raw_json)`  
- `id_map(canonical_player_id, yahoo_player_id, espn_player_id, confidence)`  
- `projections_weekly(season, week, canonical_player_id, points)`

## 6) Ingestion flows
### Yahoo sync (read‑only)
- On login: discover games and leagues for the user; persist league settings and team metadata.  
- Daily: roster, projections, player status.  
- Periodic during season: standings, waivers, transactions (read‑only).  
- Pagination: honor `count`/`start` paging where applicable. Cache responses.

### PyESPN sync
- Pre‑week: load season schedule and index event_ids.  
- Live: poll event summary + play‑by‑play for tracked event_ids at low latency. Use ETag/Last‑Modified when exposed by upstream. Persist drives/plays with sequence ordering.  
- Teams/venues: refresh weekly; keep colors/logos cached with URLs, not re‑hosted assets.

## 7) Canonicalization
- Build `id_map` using normalized name + team + position; reconcile Yahoo player keys to ESPN athlete IDs. Maintain a confidence score and allow manual overrides.

## 8) Analytics (advisory only)
- Lineup optimizer: ILP/CP-SAT maximizing Yahoo projected points within slot eligibility and lock states. Inputs only from Yahoo projections and league scoring rules.  
- Start/Sit: show marginal gains vs current lineup; expose rationale (usage trend, matchup, venue).  
- Waivers: rank free agents by Δ vs replacement over next N weeks; output FAAB guidance as advisory text.  
- Trades: VORP‑based valuation and ROS schedule sensitivity, advisory only.

## 9) Live visualization
- **Scoreboard:** score, quarter, game clock, possession, timeouts, down/distance, yardline, flag/review states.  
- **Field animation:** derive ball travel and dead‑ball spot from play fields; avoid implying player XY tracking. Tween run/pass paths, mark tackle/TD, show penalties.  
- **Overlays:** team logos and uniforms from PyESPN image/team data; venue info from PyESPN venue; weather overlays deferred until your weather guide.

## 10) API surface (backend)
- `GET /me/leagues` → user leagues and teams (Yahoo).  
- `GET /leagues/{league_key}/roster?week=` → roster + projections + optimized lineup.  
- `GET /games/live` → today’s events + basic scoreboard state (PyESPN).  
- `GET /games/{event_id}/pbp` → normalized drives/plays for animation.  
- `WS /ws/games/{event_id}` → realtime deltas for the client.

## 11) Frontend deliverables
- Dashboard: matchup card, roster compliance, injury and bye alerts.  
- Optimizer view: recommended lineup with deltas and rationale.  
- Waivers: ranked board with advisory FAAB ranges.  
- Trade evaluator: fairness score and starter impact.  
- Live Game Center: scoreboard + animated field + team/venue panels.

## 12) Testing
- Contract fixtures for Yahoo league/team/roster responses.  
- Golden samples for PyESPN Event/Drive/Play sequences across quarters and edge cases.  
- Property tests for lineup feasibility.  
- Load test WS fan‑out during Sunday windows.

## 13) Operational notes
- Respect Yahoo OAuth2 and scope limits; backoff on 429.  
- Treat PyESPN as an unofficial wrapper; add schema guards and feature flags.  
- Do not redistribute league or ESPN assets; cache by URL and respect upstream usage.  
- Weather work is out of scope in this doc; integrate when your guide is available.
