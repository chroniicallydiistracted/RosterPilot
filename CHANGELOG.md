# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
as we progress through the scaffold and implementation phases.

## [0.1.0] - 2025-10-23
### Added
- Repository-wide editor, lint, and type-check scaffolding (`.editorconfig`,
  `.pre-commit-config.yaml`, `ruff.toml`, `mypy.ini`).
- Documentation workspace (`docs/`) with development setup guidance and
  placeholders for architecture and API contracts.
- Fixtures directory placeholder aligning with the testing strategy in the
  phase plan.
- Initial project changelog.

## [0.2.0] - 2025-10-23
### Added
- PyESPN HTTP client, ingestion service, and recorded fixtures to persist
  NFL scoreboard and play-by-play data into the relational schema.
- Event state table, drive ownership metadata, and venue state details via
  Alembic migration `20251023_0003_pyespn_ingest`.
- Database-backed `/api/games/live` and `/api/games/{event_id}/pbp`
  implementations returning normalized responses from stored data.
- Unit and contract test coverage for PyESPN ingestion along with updated
  test seeding to hydrate the SQLite test database.

## [0.3.0] - 2025-10-23
### Added
- Reference seeding job that hydrates NFL teams and venues from captured ESPN
  metadata, ensuring baseline data exists before live ingestion.
- Canonical player reconciliation service, curated mapping dataset, and Alembic
  migration `20251023_0004_canonical_mapping_seed` to harden the identifier map.
- Unit tests validating the reference seeds, canonical mapping behavior, and
  Yahoo ingestion resilience to manual overrides.

## [0.4.0] - 2025-10-23
### Added
- Sliding window rate limiter enforced on Yahoo OAuth authorize/callback routes
  with coverage in integration tests.
- Request metrics collector and middleware emitting `X-Request-Duration-Ms`
  headers and enabling percentile checks against the 250 ms performance budget.
- Security CI job running Gitleaks, `pip-audit`, and `npm audit` alongside
  local developer guidance in `docs/DEV_SETUP.md`.
- Unit tests for the rate limiter and metrics utilities plus integration tests
  verifying rate-limit responses and timing instrumentation.
