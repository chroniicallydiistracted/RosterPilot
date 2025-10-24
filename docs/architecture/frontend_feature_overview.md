# Frontend Feature Overview

This document distills the feature expectations for the RosterPilot web
application so the frontend implementation stays aligned with the product
vision captured in `README.md`, `INSTRUCTIONS.md`, and
`SCAFFOLD_PHASE_PLAN.md`. It is intended for engineers and designers who
need a concise map of what the UI must deliver and which backend
contracts or environment toggles each surface depends on.

## Runtime Context

- **Framework:** Next.js (App Router) with TypeScript and PixiJS for
  canvas animation.
- **Deployment:** Cloudflare Pages consuming the FastAPI backend running
  on Google Cloud Run.
- **Environment variables:**
  - `NEXT_PUBLIC_API_URL` – base URL for REST calls (`GET /me/leagues`,
    `GET /games/live`, etc.).
  - `NEXT_PUBLIC_WS_URL` – WebSocket entrypoint for
    `/ws/games/{event_id}` live deltas.
  - `NEXT_PUBLIC_ENV` – gates optional UI (e.g., weather overlays when
    `FEATURE_WEATHER` is enabled server-side).
  - Fetch `/api/meta/config` during bootstrap to confirm heartbeat
    interval, feature flags, and websocket paths exposed by the backend.
  - Cross-origin URLs must stay in sync with backend
    `APP_BASE_URL`/`API_BASE_URL` and `CORS_ALLOWED_ORIGINS`.

## Global UX Pillars

1. **Advisory companion:** Reinforce that roster moves are suggestions
   only. Include provenance badges (Yahoo vs PyESPN) on all data-driven
   widgets.
2. **Live context:** Surface current NFL game state alongside fantasy
   insights so users can make informed decisions quickly.
3. **Accessibility:** WCAG AA color contrast, keyboard navigation for
   lineup adjustments, screen-reader friendly ARIA labels, and motion
   preferences respected during animations.
4. **Performance:** Fast initial load via static generation where
   possible, streaming data through SWR/React Query and WebSocket hooks
   for live updates.

## Feature Surfaces

### 1. Dashboard

**User goals:**
- View weekly matchup summary (fantasy score, projected vs actual).
- Track injuries, bye weeks, and lineup compliance warnings.
- Receive short advisory callouts (optimizer hints, upcoming deadlines).

**Data dependencies:**
- `GET /me/leagues` → league metadata, team roster snapshots, current
  matchup opponent.
- `GET /leagues/{league_key}/roster?week=` → enriched roster with
  optimizer deltas and compliance status.
- Cached schedule snippets from PyESPN (next kickoff times) when
  available.

**Key UI elements:**
- League selector dropdown pinned to header.
- Matchup card summarizing score, projections, and time remaining.
- Alert stack (injuries, bye, waiver deadlines) with provenance badges.
- Quick links to Optimizer, Waivers, Trade, and Live Game Center views.

### 2. Optimizer View

**User goals:**
- Compare current lineup vs recommended lineup.
- Understand rationale for each suggested swap or benching.
- Lock specific players before recalculating.

**Data dependencies:**
- `GET /leagues/{league_key}/roster?week=` response enriched with
  optimizer payload: recommended slot assignments, marginal point deltas,
  rationale bullet list, and constraint flags (e.g., positional limits).
- Local state to track locked players before calling a forthcoming
  optimizer POST/PUT endpoint (placeholder during scaffold phase).

**Key UI elements:**
- Tabular lineup view with drag-and-drop or button based slot swaps.
- Marginal gain badges per suggestion.
- Rationale drawer referencing projections, matchup difficulty, venue,
  or recent usage trends.
- Lock toggles and reset controls.

### 3. Waivers Board

**User goals:**
- Discover free agents ranked by projected impact.
- Understand FAAB recommendations and roster fit.
- Queue advisory actions for manual execution in Yahoo.

**Data dependencies:**
- Yahoo ingestion tables for free agents and projections (exposed via a
  future endpoint, likely `GET /leagues/{league_key}/waivers`).
- League scoring settings from `GET /me/leagues` to contextualize
  rankings.

**Key UI elements:**
- Filterable list (position, availability, projection window).
- Advisory chips showing recommended bid ranges and roster impact.
- Comparison sidebar to existing roster players.
- Export/share option for personal notes (no automated Yahoo actions).

### 4. Trade Evaluator

**User goals:**
- Evaluate fairness and long-term impact of proposed trades.
- Balance positional depth and schedule difficulty across teams.
- Identify risk factors (injury, bye clusters) before submitting trades
  in Yahoo.

**Data dependencies:**
- Team rosters and projections (same sources as optimizer).
- Season schedule strength data derived from PyESPN events/venues.
- Optimizer/analytics module for VORP calculations.

**Key UI elements:**
- Dual roster selectors for "My Team" and "Trade Partner".
- Drag/drop or multiselect player pickers for outgoing/incoming assets.
- Fairness meter with textual rationale.
- Impact summary (weekly delta, playoff outlook).

### 5. Live Game Center

**User goals:**
- Watch live drive/play progression for tracked NFL games.
- Monitor fantasy-relevant events (scores, injuries) in real time.
- Replay recorded games for analysis.

**Data dependencies:**
- `GET /games/live` for scoreboard snapshot and drive summaries.
- `GET /games/{event_id}/pbp` for historical context and replay mode.
- `WS /ws/games/{event_id}` for live deltas (`{sequence, clock, quarter,
  down, distance, yardline_100, type, yards, flags}`).
- Feature flags `FEATURE_REPLAY` and future `FEATURE_WEATHER` surfaced
  via backend metadata endpoints.

**Key UI elements:**
- Scoreboard header showing score, quarter, clock, possession, timeouts.
- PixiJS field canvas animating plays with adjustable playback speed and
  respect for reduced-motion settings.
- Drive timeline with jump-to-play controls.
- Team and venue panels referencing PyESPN logos/colors/venue facts.
- Optional weather banner (gated until guide lands).

## Supporting Infrastructure & Patterns

- **Navigation:** App Router layout with persistent sidebar (desktop) or
  bottom nav (mobile). All feature views share global context for the
  selected league and week.
- **State management:** Prefer SWR or React Query for REST caching,
  combined with context providers for selected league/week and user
  profile. WebSocket updates should optimistically patch cached data.
- **Error handling:** Central toast/inline alerts with fallback copy
  guiding users back to Yahoo for critical actions. Sensitive data (e.g.,
  league names) must be redacted in error surfaces per requirements.
- **Testing focus:** Jest/RTL for component behavior, Storybook visual
  baselines, and Playwright scenarios covering OAuth callback, optimizer
  flow, and live game playback (phased in alongside implementation).

## Open Questions / Future Notes

- Confirm final shape of optimizer API for lockable recommendations once
  Phase 7 lands.
- Determine how to persist user display preferences (e.g., dark mode,
  scoreboard layout) without storing PII.
- Align on animation library conventions (PixiJS scenes, texture atlas)
  before building complex play diagrams.

Document owners should update this overview as backend contracts solidify
and new product requirements emerge.
