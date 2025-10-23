# AGENTS_AND_REQUIREMENTS.md

This document merges AGENTS.md (delegation plan) and REQUIREMENTS_AGENT.md (system requirements) into one authoritative spec.

---

# AGENTS.md — Delegation Plan

**Date:** 2025-10-23  
**Scope:** Read‑only Yahoo integration. PyESPN for official NFL. Weather deferred. This document defines roles, inputs, outputs, constraints, success metrics, and handoffs for an AI coding team.

## Global Rules
- Data provenance: Yahoo → fantasy objects; PyESPN → official NFL. No cross‑inference.  
- No Yahoo write scope. Advisory only.  
- No scraping ESPN HTML. Use PyESPN only.  
- Secrets via env or vault. No credentials in repo.  
- Every PR must pass: type check, lint, unit tests, contract tests, security scan.

## Execution Order (Gated)
1. **Infra bootstrap** → 2. **Backend skeleton** → 3. **Yahoo auth + read** → 4. **PyESPN ingest** → 5. **DB schema + migrations** → 6. **Realtime hub** → 7. **Optimizer v1** → 8. **Frontend dashboard + game center** → 9. **QA hardening**.

---

## Roles

### 1) Lead Architect Agent
**Objective:** Keep scope coherent and enforce constraints.  
**Inputs:** This file, README, requirements, product goals.  
**Outputs:** ADRs, schema decisions, endpoint contracts.  
**Constraints:** Read‑only Yahoo; PyESPN only for NFL.  
**Success:** No rework across layers; stable contracts.

### 2) Backend API Agent (FastAPI)
**Objective:** Build REST and WS surfaces.  
**Inputs:** Endpoint contracts; DB schema.  
**Outputs:** `GET /me/leagues`, `GET /leagues/{league_key}/roster?week=`, `GET /games/live`, `GET /games/{event_id}/pbp`, `WS /ws/games/{event_id}`.  
**Constraints:** p95 REST < 250 ms under 50 RPS; WS fan‑out to 5k clients.  
**Handoff:** To Frontend Agent for consumption.

### 3) Yahoo Integration Agent
**Objective:** OAuth2 (fspt-r), league/team/roster/projections ingestion.  
**Inputs:** Yahoo client id/secret, redirect URI.  
**Outputs:** Normalized JSON persisted to Postgres.  
**Constraints:** Read‑only; pagination; caching.  
**Handoff:** To Optimizer and Frontend.

### 4) PyESPN Integration Agent
**Objective:** Season schedule, events, drives, plays, teams, venues.  
**Inputs:** Season year(s), tracked event_ids.  
**Outputs:** Normalized event/drive/play tables; team/venue caches.  
**Constraints:** Poll cadence live {2–5 s}; schema guards.  
**Handoff:** To Realtime Agent and Frontend.

### 5) Realtime/WS Agent
**Objective:** Publish compact deltas.  
**Inputs:** Stored plays/events or in‑memory cache.  
**Outputs:** WS messages: `{sequence, clock, quarter, down, distance, yardline_100, type, yards, flags}`.  
**Constraints:** At‑least‑once delivery, idempotent apply on client.

### 6) Optimizer Agent
**Objective:** ILP/CP‑SAT lineup recommendation using Yahoo projections and scoring.  
**Inputs:** Roster, eligibility, projections.  
**Outputs:** Recommended lineup, marginal gains, rationale.  
**Constraints:** Deterministic ≤ 5 s; feasibility under all league rules.

### 7) Frontend Agent
**Objective:** Next.js + PixiJS UI.  
**Inputs:** Backend endpoints and WS stream.  
**Outputs:** Dashboard, Optimizer, Waivers, Trade, Live Game Center.  
**Constraints:** 60 fps animations; accessible components; mobile first.

### 8) Assets Agent
**Objective:** Logos via PyESPN URLs; uniforms via templates; field PNG/SVG.  
**Inputs:** Team palettes; rulebook field specs.  
**Outputs:** Versioned assets with cache headers.  
**Constraints:** No redistribution of third‑party packs.

### 9) DevOps/Infra Agent
**Objective:** CI/CD, secrets, monitoring.  
**Inputs:** Dockerfiles, IaC.  
**Outputs:** Staging and prod deployments; metrics, alerts.  
**Constraints:** Zero secrets in repo; rollbacks < 10 min.

### 10) QA/Test Agent
**Objective:** Quality gates.  
**Inputs:** Specs and fixtures.  
**Outputs:** Unit, contract, load, visual tests; coverage reports.  
**Constraints:** Coverage ≥ 80%; zero critical vulns.

### 11) Docs Agent
**Objective:** Keep README and API docs current.  
**Outputs:** Markdown docs, OpenAPI export.  
**Constraints:** Single source of truth is README.

---

## Handoffs and Artifacts
- Backend → Frontend: OpenAPI JSON, WS message schemas, example payloads.  
- Yahoo/PyESPN → DB: Alembic migration files and seed scripts.  
- Optimizer → Frontend: schema for lineup results and rationale bullets.  
- QA → All: failing tests block merges.

## Stop Criteria
- All endpoints pass integration tests with recorded fixtures.  
- Game Center renders and animates two full real games from fixtures.  
- Optimizer returns feasible lineup for at least three league rule sets.  
- README reflects deployed architecture and constraints.



---

# REQUIREMENTS for Coding AI Agent

**Date:** 2025-10-23  
**Audience:** All engineering agents.

## Functional Requirements
1. Read‑only Yahoo integration: enumerate leagues/teams, fetch rosters, projections, standings, waivers, transactions.  
2. PyESPN ingestion: season schedule, teams, venues, events, drives, plays.  
3. Realtime WS: push compact deltas for live games.  
4. Optimizer: ILP lineup recommendation using Yahoo projections and league rules.  
5. UI: Dashboard, Optimizer, Waivers, Trade Evaluator, Live Game Center with broadcast‑style scoreboard and animations.

## Non‑Functional Requirements
- **Performance:** REST p95 < 250 ms at 50 RPS; WS broadcast supports 5k concurrent clients; animation 60 fps on modern mobile.  
- **Reliability:** Backoff and jitter on upstream errors; circuit breakers; retry with idempotency.  
- **Security:** OAuth2 tokens encrypted at rest; rotate refresh tokens; least‑privilege scope `fspt-r`. No write actions.  
- **Privacy:** Do not log PII or raw tokens. Redact league names on error paths.  
- **Compliance:** No redistribution of third‑party assets; attribution where required.  
- **Portability:** Python 3.11+, Node 20+, Postgres 15, Redis 7.  
- **Observability:** Structured logs, request tracing, metrics {fetch latency, cache hit, WS fan‑out, optimizer runtime}.  
- **Accessibility:** WCAG AA color contrast; keyboard navigation; ARIA landmarks.

## Interfaces
- Backend endpoints:  
  - `GET /me/leagues`  
  - `GET /leagues/{league_key}/roster?week=`  
  - `GET /games/live`  
  - `GET /games/{event_id}/pbp`  
  - `WS /ws/games/{event_id}`

## Data Provenance Rules
- Yahoo is authoritative for fantasy context.  
- PyESPN is authoritative for official NFL context.  
- Weather integration is deferred; leave hooks and feature flag.

## Quality Gates
- Type checks clean.  
- Lint clean.  
- Unit tests ≥ 80% coverage.  
- Contract tests pass for Yahoo and PyESPN fixtures.  
- Load test: WS broadcast to 5k clients for 10 minutes without drops.

## Deliverables
- Backend service with OpenAPI schema.  
- Frontend with functional Live Game Center and Optimizer view.  
- Alembic migrations and seed scripts.  
- Test suite with fixtures and CI pipeline.  
- Docs: README, API docs, agents plan, requirements.

## Definition of Done
- End‑to‑end demo runs with recorded fixtures.  
- User can authenticate, see leagues, run optimizer, watch two full game replays.  
- README reflects shipped behavior and constraints.  
- All quality gates green.

