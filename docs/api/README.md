# API Contracts

This folder will house OpenAPI exports, WebSocket message schemas, and
example payloads for the endpoints defined in `INSTRUCTIONS.md`.

## Planned Artifacts

- `openapi.json` – Generated from the FastAPI app
- `examples/` – Sample requests/responses for `/me/leagues`,
  `/leagues/{league_key}/roster`, `/games/live`, and
  `/games/{event_id}/pbp`
- `ws/` – Canonical message schema for `/ws/games/{event_id}` including
  delta examples

Keep fixtures anonymized and aligned with the data provenance rules.
