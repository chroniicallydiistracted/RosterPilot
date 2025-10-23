# PyESPN Integration Notes (NFL)

**Date:** 2025-10-23  
**Role:** Source of official NFL schedules, teams, rosters, events, drives, plays, images/logos, venues. Unofficial wrapper of ESPN hidden APIs.

## Key classes to use
- **Client/Sports Available**: initialize for `nfl` and load season schedule.  
- **Event**: top‑level game object; holds competitors, status, start time, venue, odds.  
- **Drive**: series possessions; start/end yardline, result, timing.  
- **Play**: atomic events with sequence order, clock, quarter, down/distance, yardline_100, type, yards, participants, flags.  
- **Team**: names, abbreviations, colors, logos (image relations).  
- **Venue**: stadium metadata including roof/surface and coordinates.

## Usage outline
1. Initialize client for NFL.  
2. Load season schedule and index event_ids.  
3. For a tracked event_id in LIVE state, call the play‑by‑play loader on a short cadence and persist drives/plays.  
4. Publish compact deltas to the frontend over WebSocket.  
5. Map ESPN teams/athletes to your canonical IDs and to Yahoo player keys via reconciliation rules.

## Performance and stability
- Use short TTL caching for scoreboard/state.  
- Persist raw play records for auditability, plus normalized columns for animation.  
- Expect schema drift. Guard for missing or renamed fields; do not assume every play has identical attributes.

## Assets
- Consume logo/image URLs from the Team/Image relations. Store URLs only; fetch via your proxy with cache controls.  
- Uniforms: derive simple home/away templates from team color palettes if needed; do not redistribute third‑party packs.

## Weather
- You confirmed weather is present in stadium/matchup JSON. Defer implementation details until your weather guide is published. Keep a placeholder to read those fields when available.
