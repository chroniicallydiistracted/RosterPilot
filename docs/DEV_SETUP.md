# Local Development Setup

RosterPilot spans a FastAPI backend, a Next.js frontend, and shared
infrastructure components. Follow these steps to stand up a consistent
development environment.

## 1. Prerequisites

- Python 3.11+
- Node.js 20+
- Poetry (`pip install poetry`)
- Docker Desktop (optional but recommended for parity with Cloud Run)

## 2. Environment Variables

Consult `ENVIRONMENT_VARIABLES.md` for the full catalog. At minimum,
create the following files from the provided templates:

- `cp backend/.env.example backend/.env`
- `cp frontend/.env.production.example frontend/.env.local`

Populate the secrets using the values issued by Yahoo, Neon, and
Upstash. Never commit filled `.env` files.

## 3. Backend Setup

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload
```

This boots the FastAPI app with hot reload. Uvicorn will read the env
values from `backend/.env` when running locally.

## 4. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The Next.js dev server proxies API requests to the backend via
`NEXT_PUBLIC_API_URL`. Adjust the value in `.env.local` if needed.

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
