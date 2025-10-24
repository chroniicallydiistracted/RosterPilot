# Local Development Setup

RosterPilot spans a FastAPI backend, a Next.js frontend, and shared
infrastructure components. Follow these steps to stand up a consistent
development environment.

## 1. Prerequisites

- Python 3.11+
- Node.js 20+ (with npm 10+)
- Poetry 1.8 (`pip install "poetry==1.8.3"`)
- Docker Desktop (optional but recommended for parity with Cloud Run)

## 2. Environment Variables

Consult `ENVIRONMENT_VARIABLES.md` for the full catalog. At minimum,
create the following files from the provided templates:

- `cp backend/.env.example backend/.env`
- `cp frontend/.env.example frontend/.env.local`

Populate the secrets using the values issued by Yahoo, Neon, and
Upstash. Never commit filled `.env` files.

## 3. Backend Setup

```bash
cd backend
poetry install --with dev --sync
poetry run rp-env-check  # optional sanity check
poetry run uvicorn app.main:app --reload
```

This boots the FastAPI app with hot reload using the pinned dependency
set from `poetry.lock`. The optional `rp-env-check` command validates the
environment variables via the `Settings` schema.

## 4. Frontend Setup

```bash
npm install
npm run dev --workspace frontend
```

The workspace-aware install keeps a single `package-lock.json` at the
repo root. Update `frontend/.env.local` if the backend runs on a
different host.

## 5. Database and Redis

For local development you can either:

1. Point to staging instances provided by the team, or
2. Run disposable containers via Docker:

```bash
docker run --rm -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15
# Use a Redis image compatible with Upstash features if needed
```

Remember to keep the read/write separation and scope described in the
project docs—no Yahoo write actions.

## 6. Tooling & Quality Gates

Install pre-commit hooks to align with CI:

```bash
pip install pre-commit
pre-commit install
```

Available npm/pnpm/yarn scripts at the repo root:

- `npm run lint` – Executes frontend ESLint and backend Ruff/Mypy.
- `npm run test` – Placeholder hook for backend pytest and frontend Jest.
- `poetry run pip-audit` (from `backend/`) and `npm audit --omit=dev --audit-level=high`
  surface dependency vulnerabilities locally before CI.

Keep lint, type checks, and tests green before opening pull requests.
