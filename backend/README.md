# Backend Service Scaffold

This directory contains the FastAPI backend for RosterPilot. The initial scaffold establishes the
packages, configuration modules, and dependency entry points that will power the Yahoo and PyESPN
integrations, the optimizer, and supporting infrastructure.

## Layout

- `app/`
  - `main.py` – FastAPI application factory and router wiring.
  - `api/` – REST routers grouped by resource (health, me, leagues, games).
  - `clients/` – HTTP clients and SDK wrappers for Yahoo, PyESPN, and Redis.
  - `core/` – Configuration and common utilities (environment settings, logging, telemetry).
  - `dependencies/` – FastAPI dependency providers (database sessions, settings, auth contexts).
  - `jobs/` – Background scheduling and ingestion jobs (Celery/APScheduler stubs).
  - `models/` – SQLAlchemy model declarations and metadata helpers.
  - `optimizer/` – Lineup optimization engine (OR-Tools/CP-SAT stubs).
  - `schemas/` – Pydantic request/response models shared across routers and services.
  - `services/` – Application service layer encapsulating business rules.
  - `ws/` – WebSocket router and realtime broadcasting utilities.
- `clients/`, `models/`, `optimizer/`, and `tests/` directories each contain `.gitkeep` or placeholder
  files so they remain tracked until populated with concrete implementations.
- `pyproject.toml` configures Poetry for dependency management targeting Python 3.11.
- `Dockerfile` packages the FastAPI service for Google Cloud Run deployments.

## Next Steps

1. Flesh out database models and Alembic migrations once schemas are finalized.
2. Implement Yahoo OAuth + ingestion clients inside `app/clients/yahoo.py`.
3. Populate PyESPN ingestion inside `app/clients/pyespn.py` and supporting services.
4. Expand the FastAPI routers under `app/api/routes/` for leagues, rosters, and games.
5. Introduce CI workflows that build the Docker image defined here and run lint/type/test suites.
