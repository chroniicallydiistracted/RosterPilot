# Yahoo Fantasy Sports API — Read‑Only Consumption

**Date:** 2025-10-23  
**Scope:** `fspt-r` only. No write actions.

## Auth
- OAuth 2.0 Authorization Code flow. Register app, set redirect URI, request `fspt-r`.  
- Store access + refresh tokens. Refresh proactively before expiry.  
- Handle user revocation by re‑auth prompt.

## Core resource pathing (JSON)
- Base: `https://fantasysports.yahooapis.com/fantasy/v2/` with `?format=json` where supported.  
- Discover leagues for the logged‑in user: `/users;use_login=1/games` then filter NFL.  
- League metadata: `/league/{league_key}` → settings, scoring, standings, transactions.  
- Team + roster: `/team/{team_key}` → roster, eligible positions, week stats.  
- Players: `/players;player_keys=...` or `/players;search=...` for availability and metadata.  
- Projections and actuals: player/team stats subresources structured by week/scoring period.

## Ingestion cadence (read‑only)
- On login: enumerate leagues/teams; persist league rules.  
- Daily: roster, projections, player status.  
- In‑season periodic: standings, waivers, transactions (read‑only).

## Pagination and hygiene
- Some collections page in batches (commonly 25) with a `start` offset parameter. Loop until empty.  
- Cache league‑static metadata with long TTL; roster/projections with shorter TTL around lock.

## Data separation policy
- Fantasy constructs (lineup slots, projections, roster, waivers, trades, standings) → Yahoo.  
- Official NFL constructs (schedule, game state, pbp, teams, venues, logos) → PyESPN.  
- Do not cross‑infer fields; keep provenance clear in your UI labels and logs.
