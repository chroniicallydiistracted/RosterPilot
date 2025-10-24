# Dependency Hardening Summary

## Inventory Snapshot
- **Backend (FastAPI)** – `backend/` (Poetry, Dockerfile, tests, Alembic config). 【F:backend/pyproject.toml†L1-L37】【F:backend/Dockerfile†L1-L43】
- **Frontend (Next.js)** – `frontend/` (workspace-managed by npm, lint/test suites). 【F:frontend/package.json†L1-L37】
- **Shared tooling & docs** – repo root scripts (`devstartup.sh`), documentation (`docs/`), CI workflows (`.github/workflows/ci.yml`). 【F:devstartup.sh†L1-L66】【F:.github/workflows/ci.yml†L1-L69】
- **Infrastructure notes** – `infrastructure/` for provider guidance. 【F:infrastructure/README.md†L1-L20】

## Package Managers & Lockfiles
- **Python:** Poetry 1.8 with in-project virtualenvs (`backend/pyproject.toml`, `backend/poetry.lock`). 【F:backend/pyproject.toml†L1-L37】
- **Node.js:** npm workspaces with a single root lockfile (`package.json`, `package-lock.json`, `frontend/package.json`). 【F:package.json†L1-L35】【F:frontend/package.json†L1-L37】

## Security & Version Hygiene
- Resolved Next.js high-severity advisories by upgrading the frontend to Next 15.5.6 and aligning eslint tooling. Final `npm audit --omit=dev` reports zero vulnerabilities. 【F:frontend/package.json†L8-L28】【79c78c†L1-L3】
- Upgraded FastAPI stack (FastAPI 0.120.0, Starlette 0.48.0, Cryptography 44.0.1) to clear backend CVEs reported by `pip-audit`. 【F:backend/pyproject.toml†L11-L29】【7948c3†L1-L2】
- Added deterministic Poetry export + pip-audit flow in CI to gate dependency drift. 【F:.github/workflows/ci.yml†L33-L68】

## Hardened Install Paths
- Backend Dockerfile now uses a builder stage that exports Poetry requirements and installs with pinned `pip==24.2`, improving cache hits and reproducibility on Cloud Run. 【F:backend/Dockerfile†L1-L43】
- Root scripts and docs instruct `poetry install --with dev --sync`, `npm install`, and workspace-aware commands for consistent local and CI setups. 【F:devstartup.sh†L1-L66】【F:docs/DEV_SETUP.md†L1-L60】【F:README.md†L141-L156】
- CI caches Poetry and npm artifacts, runs lint/tests, and executes security scans with the hardened install commands. 【F:.github/workflows/ci.yml†L9-L68】

## Environment Handling
- Added service-scoped environment templates (`backend/.env.example`, `frontend/.env.example`) and documented usage in setup guides. 【F:backend/.env.example†L1-L32】【F:frontend/.env.example†L1-L4】【F:docs/ENVIRONMENT_VARIABLES.md†L100-L124】
- Exposed `rp-env-check` CLI to validate configuration via Pydantic before bootstrapping. 【F:backend/pyproject.toml†L32-L34】【F:backend/app/cli.py†L1-L24】

## Additional Developer Experience Improvements
- Converted frontend linting to `eslint` CLI to avoid deprecated `next lint` flow while keeping existing `.eslintrc` rules. 【F:frontend/package.json†L5-L13】
- Implemented tested frontend helpers (`frontend/lib/url.ts`, `frontend/lib/roster-utils.ts`, `frontend/lib/api-types.ts`) matching unit expectations for roster utilities. 【F:frontend/lib/url.ts†L1-L21】【F:frontend/lib/roster-utils.ts†L1-L41】【F:frontend/lib/api-types.ts†L1-L28】

## Recommended Follow-Ups
- Monitor FastAPI release notes for additional Pydantic 2 deprecation warnings (`model_fields` access) and refactor when convenient. 【F:backend/app/core/config.py†L104-L118】
- Consider migrating to ESLint flat config before ESLint 9 becomes default in tooling to preempt deprecation warnings. 【F:frontend/package.json†L5-L13】
