# Roster Pilot Fantasy Football Companion

Roster Pilot is a web experience that wraps Yahoo Fantasy Football league data with official NFL game telemetry to deliver actionable coaching decisions, cinematic live game visualizations, and holistic roster strategy. This README summarizes what the product is, the flows it supports, and the architecture that powers it so new contributors and stakeholders can quickly align on the vision.

---

## Product Narrative

### Vision
**Help every fantasy manager pilot their roster with confidence.** Roster Pilot keeps users informed before, during, and after every matchup. We do this by:

1. Normalizing Yahoo roster, waiver, and scoring settings to present clean, league-aware guidance.
2. Streaming official PyESPN play-by-play to immerse users in live game context while preserving advisory-only boundaries.
3. Combining projections, matchup context, and optimizer insights into transparent recommendations that respect every league's unique rules.

### Target Personas
- **Competitive Manager:** Wants weekly lineup edges, waiver foresight, and confidence in trade proposals.
- **Commissioner:** Needs high-level visibility into league health, rosters, and live scoring to keep the community engaged.
- **Live Game Enthusiast:** Follows Sunday action on the couch and craves real-time updates with rich visuals and provenance.

### Guiding Principles
- **Advisory Only:** Users execute roster changes in Yahoo; we never take write actions on their behalf.
- **Explain Every Recommendation:** Optimizer output is paired with rationale, projections, and risk markers.
- **Respect Data Provenance:** Every data panel badges its source so trust is preserved.
- **Performance Under Pressure:** Live visualizations sustain 60 fps with minimal latency during peak NFL windows.

---

## User Journeys

### 1. Onboard & Connect League
1. Sign in with Yahoo OAuth (`fspt-r` scope) and grant read access.
2. App ingests league metadata, roster slots, and scoring rules.
3. Dashboard presents active leagues with status badges and quick links.

### 2. Set a Winning Lineup
1. Select a league to view current roster, injury designations, and matchup projections.
2. Run the **Roster Optimizer** to evaluate start/sit decisions against league scoring.
3. Review suggested lineup, positional alternatives, and marginal point gains.
4. Copy recommendations into the Yahoo app (with deep links) and mark the decision as applied for tracking.

### 3. Dominate the Waiver Wire
1. Visit the **Waiver Radar** tab to see prioritized adds with recommended FAAB bids.
2. Filter by position, bye week, or projected usage spikes.
3. Explore each player card for news, matchup grades, and roster impact simulation.

### 4. Evaluate Trades Collaboratively
1. Launch the **Trade Evaluator** and select proposed players or pick assets.
2. View balance charts, positional needs, and rest-of-season (ROS) outlook.
3. Share the generated summary with league mates to facilitate transparent negotiations.

### 5. Experience Live Game Center
1. Enter **Game Center** during live NFL action.
2. Watch an interactive field powered by PixiJS render drives, plays, and scoring updates in near real time.
3. Switch between matchups, follow fantasy impact overlays, and receive optimizer nudges if a bench player is outperforming expectations.

---

## Feature Deep Dive

| Area | Description | Key Data Inputs | Primary Outputs |
|------|-------------|-----------------|-----------------|
| **League Hub** | Unified overview of all connected Yahoo leagues, with health status, upcoming matchups, and transaction alerts. | Yahoo league metadata, standings, waiver transactions. | League cards, alert feed, next steps checklist. |
| **Roster Analyzer** | Position-by-position roster breakdown with projections, matchup context, and bench comparisons. | Yahoo roster, PyESPN opponent metrics, injury feeds. | Position scorecards, replacement-level deltas, risk flags. |
| **Optimizer** | Deterministic ILP/CP-SAT solver that maximizes projected points under league roster constraints. | League scoring rules, eligible positions, projections, injuries. | Suggested lineup, bench swaps, explanation bullets, confidence score. |
| **Waiver & Trade Advisory** | Prioritized recommendations with scenario planning for adds/drops and trades. | Waiver availability, projections, schedule strength, user roster composition. | FAAB bid guidance, trade balance charts, roster impact simulation. |
| **Live Game Center** | Broadcast-style experience combining official play-by-play with fantasy impact overlays. | PyESPN events/drives/plays, Yahoo scoring updates. | Animated field, drive timelines, live fantasy score deltas, WS notifications. |
| **Insights & Notifications** | Personalized nudges and weekly recaps delivered via web UI and optional email. | Aggregated roster performance, projections, injury reports. | Actionable alerts with provenance badges and deep links. |

---

## Experience Design

- **Information Hierarchy:** Critical decisions (start/sit, waivers, trades) appear above fold with contextual tooltips. Secondary analytics (usage trends, ROS charts) are discoverable via expandable panels.
- **Visual Language:** Clean dark-on-light theme meeting WCAG AA contrast, with team colors used sparingly for highlights. Field visualizations leverage team palettes while maintaining accessibility overlays for colorblind users.
- **Interaction Model:** All flows are mobile-first with adaptive layouts. Critical tasks are accessible via keyboard navigation, and ARIA roles describe dynamic components like the live play ticker.
- **Trust Indicators:** Each card displays the data source (Yahoo, PyESPN) and timestamp of last refresh. Optimizer outcomes include model version and projected variance.

---

## System Architecture Overview

```
Yahoo OAuth & APIs ---> Yahoo Ingestor ---\
                                        |--> Postgres (league, roster, scoring)
PyESPN API ----------> PyESPN Ingestor --/
                                        |
                                        +--> Redis (live cache, WS fan-out)

Postgres + Redis --> FastAPI Backend --> REST (Next.js data fetching)
                                         └--> WebSocket Deltas (live game center)

FastAPI Optimizer Endpoint --> ILP Solver (CP-SAT) --> Recommendations

Next.js Frontend --> PixiJS Field Renderer + React UI --> User Interactions
```

- **Backend Services:** FastAPI handles REST endpoints (`/me/leagues`, `/leagues/{league_key}/roster`, `/games/live`, `/games/{event_id}/pbp`) and a WebSocket hub (`/ws/games/{event_id}`) for live deltas. Optimizer runs as an internal module with deterministic seeds to ensure reproducible output.
- **Data Layer:** Postgres stores normalized league and player data; Redis powers low-latency caches and pub/sub for live play updates. Alembic migrations manage schema evolution.
- **Frontend:** Next.js (App Router) serves authenticated routes, integrates with Yahoo OAuth callback flow, and renders PixiJS canvases for live plays. Zustand (or Redux Toolkit) manages client state alongside React Query for data synchronization.
- **Observability:** Structured logging, OpenTelemetry tracing, metrics dashboards (latency, cache hit rate, optimizer runtime), and alerting thresholds for upstream API failures.

---

## Data Provenance & Compliance

- **Yahoo Fantasy (Authoritative for fantasy context):** leagues, teams, rosters, projections, standings, waivers, transactions. Scope limited to `fspt-r` read-only permissions.
- **PyESPN (Authoritative for official NFL context):** schedules, teams, venues, play-by-play, drive data, logos, uniform metadata.
- **Weather (Deferred):** Hooks exist for ingesting stadium/matchup weather once a compliant provider is approved.
- **Privacy & Security:** OAuth tokens stored encrypted at rest. Logs redact PII and secrets. No third-party asset redistribution; all logos fetched via licensed URLs with caching headers.

---

## Development Workflow

1. **Prerequisites:** Python 3.11+, Node 20+, Postgres 15, Redis 7.
2. **Environment Variables:**
   - `YAHOO_CLIENT_ID`, `YAHOO_CLIENT_SECRET`, `YAHOO_REDIRECT_URI`
   - `DATABASE_URL`, `REDIS_URL`
   - Optional feature flags: `ENABLE_WEATHER=false`, `OPTIMIZER_SEED`
3. **Setup:**
   - Install backend dependencies with Poetry (`cd backend && poetry install --with dev --sync`).
   - Validate env configuration (`poetry run rp-env-check`) and run migrations (`poetry run alembic upgrade head`).
   - Install frontend dependencies from the repo root (`npm install`) to hydrate the workspace lockfile.
4. **Run Services:**
   - Start backend (`cd backend && poetry run uvicorn app.main:app --reload`).
   - Start frontend (`npm run dev --workspace frontend`).
   - Optional: launch websocket replay using fixtures for Game Center smoke testing.
5. **Quality Gates:**
   - `ruff`, `mypy`, `pytest`, contract tests against recorded Yahoo/PyESPN fixtures.
   - Load test WebSocket fan-out (5k clients) before release candidates.

---

## Directory Highlights

- `backend/` – FastAPI application, Yahoo & PyESPN clients, optimizer modules, websocket hub, Alembic migrations.
- `frontend/` – Next.js app, PixiJS field components, UI design system, state management.
- `docs/` – Product specifications, integration notes, architectural decision records.
- `fixtures/` – Recorded payloads for deterministic tests and demo replays.
- `infrastructure/` – Terraform, Dockerfiles, CI/CD pipeline definitions.

---

## Roadmap Snapshot

- **Weather Overlay (Feature Flagged):** Integrate stadium weather feeds to augment live visuals and waiver analysis.
- **Multi-League Insights:** Cross-league alerting and scheduling conflict detection.
- **Advanced Trading Models:** Incorporate Monte Carlo season simulations to gauge playoff odds impact.
- **Personalized Notifications:** Email/web push digests summarizing weekly performance and recommended actions.

---

## Contributing & Support

- Follow the coding standards defined in `AGENTS.md` and the repository lint/type-check requirements.
- Open pull requests with clear descriptions, attach fixtures where relevant, and ensure automated tests pass.
- Report issues via GitHub with reproduction steps, affected league IDs (redacted), and logs without secrets.

Roster Pilot thrives on collaboration. Whether you are enhancing the optimizer, refining live visualizations, or extending documentation, this README is your compass for understanding the product we are building together.
