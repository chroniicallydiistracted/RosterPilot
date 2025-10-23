# RosterPilot Build Scaffold & Phase Plan

**Date:** 2025-10-23  
**Audience:** Engineering team (architecture, backend, frontend, data, QA)  
**Scope:** Initial delivery of the Yahoo + PyESPN fantasy companion within the read-only constraints defined in `AGENTS.md`, `INSTRUCTIONS.md`, and supporting docs.

---

## 0. Guiding Principles
- Maintain strict data provenance: Yahoo for fantasy constructs, PyESPN for official NFL.  
- Read-only Yahoo scope (`fspt-r`). OAuth secrets never stored in repo; use environment variables.  
- Fast iteration with quality gates: lint, type check, unit, contract tests, security scan.  
- CI/CD ready from day one; deploy targets per `DEPLOYMENT.md` (Cloud Run backend, Cloudflare Pages frontend).

---

## 1. Repository Scaffold

### 1.1 Directory Layout
- `backend/`
  - `app/` FastAPI application package.
    - `main.py` FastAPI entry point.
    - `api/` routers for REST endpoints (`me`, `leagues`, `games`).
    - `ws/` WebSocket router and broadcast logic.
    - `dependencies/` shared dependencies (DB session, auth context).
    - `schemas/` Pydantic models for requests/responses.
    - `services/` domain logic (Yahoo ingest, PyESPN ingest, optimizer, roster analysis).
    - `jobs/` background tasks (ingestion schedulers via Celery/APS scheduler or Cloud Run job triggers).
    - `config.py` settings management (Pydantic `BaseSettings`).
  - `clients/`
    - `yahoo.py` OAuth handler + API client (read-only).
    - `pyespn.py` PyESPN wrappers and normalization utilities.
    - `redis.py` Upstash Redis publisher/subscriber.
  - `models/` SQLAlchemy models aligned with `INSTRUCTIONS.md` minimal schema.
  - `migrations/` Alembic migrations.
  - `optimizer/` ILP/CP-SAT lineup optimization module.
  - `tests/`
    - `unit/`, `integration/`, `contract/`, `fixtures/` (Yahoo & PyESPN JSON samples).
  - `pyproject.toml` (Poetry) or `requirements.txt` + `setup.cfg`.
  - `Dockerfile` targeting Cloud Run (per `DEPLOYMENT.md`).

- `frontend/`
  - `app/` or `pages/` Next.js routes.
  - `components/`
    - Dashboard widgets, lineup optimizer UI, waiver/trade cards, live game center modules.
  - `hooks/` data fetching (SWR/React Query) and WebSocket hooks.
  - `lib/` API client wrappers, provenance badges.
  - `styles/` global and component styles (Tailwind or CSS modules).
  - `public/` static assets (field SVG, placeholders) respecting licensing.
  - `tests/`
    - Unit (Jest/RTL), integration (Playwright/Cypress) as roadmap.
  - `next.config.js`, `tsconfig.json`, `package.json` with scripts for lint/test/build.

- `docs/`
  - Existing docs plus new ADRs, API contracts, and schema diagrams.
  - `architecture/` diagrams (C4, data flow).
  - `api/` OpenAPI export + client docs.

- `infrastructure/`
  - Terraform or Pulumi definitions (future).  
  - GitHub Actions workflows for backend/frontend CI/CD.

### 1.2 Configuration & Tooling
- Root `.editorconfig`, `.pre-commit-config.yaml`, `.flake8`/`ruff.toml`, `pyproject.toml` (if using Poetry) to enforce style.
- Node tooling: ESLint, Prettier, TypeScript strict mode.
- Testing harness: pytest, coverage, httpx, respx for backend; Jest, Testing Library, Playwright for frontend.
- Security: `pip-audit`, `npm audit`, secret scanning via CI.

---

## 2. Phase Plan (aligned with gated execution order)

### Phase 1 — Infra Bootstrap
- Initialize repo scaffold directories with placeholder `README`s and tool configs.
- Configure Poetry or pipenv for backend; npm/yarn for frontend.
- Add Dockerfile (backend), `.dockerignore`, base `.env` support (Pydantic settings).
- Establish CI pipeline skeleton (GitHub Actions) running lint, type check, tests on stubs.
- Document local dev workflow in `docs/DEV_SETUP.md`.

**Exit criteria:** Clean lint/type/test on scaffolds; CI green; baseline Docker image builds.

### Phase 2 — Backend Skeleton (FastAPI)
- Implement FastAPI app with health endpoints (`/healthz`, `/readyz`).
- Wire SQLAlchemy with Postgres URL, create base models per minimal schema (no logic yet).
- Stub routers for required endpoints returning mock data.
- Configure dependency injection (auth context placeholder, DB session).
- Implement Alembic initial migration matching schema skeleton.
- Add contract tests verifying endpoint structure & OpenAPI generation.

**Exit criteria:** Backend serves OpenAPI spec; endpoints return validated stub responses; migrations apply locally.

### Phase 3 — Yahoo Auth + Read Model
- Implement Yahoo OAuth flow (authorization URL, callback handling, token storage encrypted).
- Build `clients.yahoo` wrapper with pagination, rate limiting, caching.
- Ingest user leagues, teams, rosters, projections; persist to DB tables.
- Expose `GET /me/leagues` and `GET /leagues/{league_key}/roster?week=` returning normalized JSON with optimizer placeholder.
- Add fixtures and contract tests using recorded Yahoo responses.

**Exit criteria:** Auth flow completes locally; league/roster endpoints backed by DB data; tests validate ingestion.

### Phase 4 — PyESPN Ingestion
- Wrap PyESPN client for schedule, events, teams, venues, drives, plays.
- Persist normalized records to `events`, `teams`, `venues`, `drives`, `plays` tables.
- Implement `GET /games/live` and `GET /games/{event_id}/pbp` using ingested data.
- Add caching (Redis) and guards for schema drift; include logging & metrics.
- Expand contract tests with PyESPN fixtures covering live and completed games.

**Exit criteria:** API surfaces game schedule and PBP data from DB; ingestion handles incremental updates; tests pass.

### Phase 5 — Database Schema Hardening & Migrations
- Finalize canonical player ID mapping (Yahoo ↔ ESPN) with reconciliation logic.
- Implement projections table, indexes, and constraints.
- Create seeding scripts for baseline data (team colors, venues).
- Add DB unit tests, property tests on data integrity.

**Exit criteria:** Schema stable with migrations; canonical ID map operational; tests enforce referential integrity.

### Phase 6 — Realtime Hub (WebSockets)
- Build Redis pub/sub or async queue for live deltas.
- Implement `/ws/games/{event_id}` WebSocket broadcasting compact delta payloads `{sequence, clock, quarter, down, distance, yardline_100, type, yards, flags}`.
- Add heartbeat/ping configuration (`WS_HEARTBEAT_SEC`).
- Provide replay mode using stored plays for deterministic playback.
- Load test WS fan-out (local harness) to validate design.

**Exit criteria:** WebSocket streams derived deltas with idempotent sequence; load tests meet 5k client target.

### Phase 7 — Optimizer v1
- Implement lineup optimizer using OR-Tools CP-SAT (or PuLP fallback) referencing Yahoo projections.
- Encode league roster slots, locked players, bench constraints.
- Surface optimizer results via `/leagues/{league_key}/roster?week=` including marginal gains & rationale stubs.
- Add unit tests for multiple league rule sets; ensure deterministic output ≤5s.

**Exit criteria:** Optimizer returns valid lineup & diff metrics; tests cover sample leagues; performance meets spec.

### Phase 8 — Frontend Dashboard & Game Center
- Scaffold Next.js app with shared layout and authentication flow (OAuth redirect handler).
- Implement data fetching hooks (SWR/React Query) for REST endpoints and WS integration.
- Build UI views: Dashboard, Optimizer, Waivers, Trade, Live Game Center (PixiJS field).
- Integrate provenance badges (Yahoo vs PyESPN). Ensure WCAG AA compliance.
- Add frontend testing (Jest + RTL) and visual regression (Storybook/Chromatic optional).

**Exit criteria:** Frontend renders data from live backend stubs; game center animates sample fixtures; accessibility checks pass.

### Phase 9 — QA Hardening & Pre-Launch
- Expand integration tests spanning OAuth → ingest → optimizer → WS playback.
- Security audit (dependency scanning, secret detection, rate limiting tests).
- Performance profiling (REST p95 < 250 ms @ 50 RPS, WS broadcast 5k clients).
- Documentation updates: OpenAPI export, runbooks, troubleshooting.
- Prepare staging deployment pipeline per `DEPLOYMENT.md`.

**Exit criteria:** All quality gates satisfied; staging environment mirrors production; documentation current.

---

## 3. Cross-Cutting Concerns
- **Observability:** Implement structured logging, OTLP exporters, Sentry instrumentation across backend and frontend.
- **Secrets Management:** Use Google Secret Manager & Cloudflare secrets; never commit real credentials.
- **Feature Flags:** `FEATURE_WEATHER`, `FEATURE_REPLAY`, `NEXT_PUBLIC_ENV` to gate optional functionality.
- **Accessibility & UX:** Conduct keyboard navigation tests; ensure contrast ratios; provide explanatory tooltips.
- **Compliance:** Attribute data sources; ensure no redistribution of assets.

---

## 4. Deliverables Timeline (High-Level)
| Week | Focus | Key Milestones |
|------|-------|----------------|
| 1 | Phases 1–2 | Repo scaffold, CI, backend skeleton, health endpoints |
| 2 | Phase 3 | Yahoo OAuth, ingest, roster endpoints |
| 3 | Phase 4 | PyESPN ingestion, game endpoints |
| 4 | Phases 5–6 | Schema hardening, realtime hub MVP |
| 5 | Phase 7 | Optimizer implementation, tests |
| 6 | Phase 8 | Frontend UI integration, accessibility checks |
| 7 | Phase 9 | QA hardening, staging deploy, documentation |

*Adjust timeline based on team velocity and integration findings.*

---

## 5. Immediate Next Steps
1. Approve this scaffold & phase plan.
2. Generate baseline repo structure (`backend/`, `frontend/`, `docs/`, `infrastructure/`).
3. Implement Phase 1 tasks (tooling, CI, environment setup, `.env` files).
4. Schedule dependencies (Yahoo OAuth credentials, Neon DB instance, Upstash Redis) for Phase 3 readiness.

---

Prepared by: **Lead Architect Agent**
