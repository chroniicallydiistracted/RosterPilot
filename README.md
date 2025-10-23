# Yahoo + PyESPN Fantasy Companion

**Date:** 2025-10-23  
**Mission:** Advisory companion for Yahoo Fantasy Football. Read‑only Yahoo scopes. Official NFL game data from PyESPN. Live, broadcast‑style visualization plus lineup optimization and roster guidance.

## Vision
A fast, reliable companion that improves weekly outcomes through clear guidance and live context. Users keep full control by executing changes in the Yahoo app. The app never writes to Yahoo.

## Sources of Truth
- **Yahoo (fantasy):** leagues, teams, rosters, projections/actuals, standings, waivers, transactions.  
- **PyESPN (NFL):** schedules, teams, venues, logos, events, drives, plays.  
- **Weather:** deferred; consume embedded stadium/matchup weather when enabled by separate guide.

## Core Features
- League discovery and roster views.  
- Start/Sit optimizer using Yahoo projections and league rules.  
- Waiver and trade advisories with transparent rationale.  
- Live Game Center with scoreboard and animated play diagrams.  
- Team logos, uniforms, and venue panels sourced via PyESPN data.  
- Provenance badges on UI elements to show data origin.

## Architecture
- **Frontend:** Next.js + TypeScript, PixiJS canvas for field animation, WS client for deltas.  
- **Backend:** FastAPI, Postgres, Redis. Ingestors for Yahoo and PyESPN. Realtime WS hub. Optimizer service.  
- **Data:** Normalized tables for leagues/teams/players and events/drives/plays. Canonical player id map.

## Boundaries
- Yahoo scope: `fspt-r` only. No writes.  
- ESPN HTML not scraped. PyESPN only.  
- Assets cached by URL; no redistribution.  
- Weather work is feature‑flagged and documented separately.

## Getting Started (Dev)
1. Python 3.11+, Node 20+.  
2. Set env vars:  
   - `YAHOO_CLIENT_ID`, `YAHOO_CLIENT_SECRET`, `YAHOO_REDIRECT_URI`  
   - `DATABASE_URL`, `REDIS_URL`  
3. Run DB migrations.  
4. Start backend (FastAPI) and frontend (Next.js).  
5. Authenticate via Yahoo OAuth; verify `/me/leagues`.  
6. Load season schedule via PyESPN and start a recorded game replay to validate the Game Center.

## Directory Layout
- `backend/` FastAPI app, clients, optimizer, ws hub, migrations.  
- `frontend/` Next.js app, components, PixiJS field, pages.  
- `docs/` This README, INSTRUCTIONS.md, PYESPN_NOTES.md, YAHOO_API_NOTES.md, AGENTS.md, REQUIREMENTS_AGENT.md.  
- `fixtures/` Recorded Yahoo and PyESPN JSON for tests.

## Quality and Operations
- Tests and lint required for merge.  
- Logs are structured; secrets never logged.  
- Metrics: fetch latency, cache hit ratio, WS fan‑out, optimizer runtime.  
- Rollback in under 10 minutes via blue‑green.

## Roadmap
- Weather overlay using embedded stadium JSON fields.  
- ROS projections enhancements.  
- More league rule variants and edge‑case support.  
- Multi‑league dashboard.

## License and Compliance
- Respect Yahoo and ESPN usage terms. Advisory only.  
- Trademarks belong to their owners. Assets used for identification only.

