# DEPLOYMENT.md — RosterPilot Production Stack Guide

**Date:** 2025-10-23  
**App:** RosterPilot – Yahoo Fantasy Football Companion  
**Audience:** Advanced Coding AI Agent  
**Scope:** End-to-end production deployment using low-cost, high-quality modern platforms

---

## Overview

**Frontend:** Cloudflare Pages  
**Backend (API + WS):** Fly.io (FastAPI)  
**Database:** Neon (Postgres)  
**Cache/PubSub:** Upstash Redis  
**Assets (logos, fields, uniforms):** Cloudflare R2  
**DNS + TLS + Proxy:** Cloudflare DNS

Designed for high-quality performance, WebSocket support, real-time game updates, and read-only Yahoo API integration.

---

## 1. Cloudflare Pages (Frontend)

### Stack:
- Next.js
- Hosted statically
- Auto-build via Git

### Setup:
1. Connect GitHub repo to Cloudflare Pages.
2. Set build command: `npm run build`
3. Set output directory: `.next`
4. Environment vars:
   - `NEXT_PUBLIC_API_URL=https://api.rosterpilot.app`
5. Custom domain: `app.rosterpilot.app`
6. TLS: Auto HTTPS via Cloudflare

---

## 2. Fly.io (Backend)

### Stack:
- FastAPI (ASGI)
- WebSocket live game updates
- Deployed via Docker

### Setup:
1. `fly launch` in `/backend` dir.
2. Select PHX region (or nearest).
3. Fly.toml:
   ```toml
   [env]
   DATABASE_URL="postgres://..."
   REDIS_URL="rediss://..."
   YAHOO_CLIENT_ID=""
   YAHOO_CLIENT_SECRET=""
   YAHOO_REDIRECT_URI="https://app.rosterpilot.app/oauth/callback"
   ```

4. Expose port 8080.
5. WebSocket support: Fly supports ASGI.
6. Health check: `/healthz`
7. TLS: Auto HTTPS
8. Custom domain: `api.rosterpilot.app` via Cloudflare DNS

---

## 3. Neon (Postgres)

### Stack:
- Postgres 15+
- Serverless, scales to zero
- 100 CU-hours free

### Setup:
1. Create project at neon.tech.
2. Create branch and database.
3. Use pooled connection string for FastAPI.
4. Run Alembic migrations.
5. Turn on PITR + daily backups.

---

## 4. Upstash Redis (Cache + PubSub)

### Stack:
- Redis 7+
- Low-throughput, pubsub
- TLS supported

### Setup:
1. Go to https://console.upstash.com
2. Create free Redis instance.
3. Copy TLS `rediss://` URL.
4. Use in backend `REDIS_URL`.
5. Use `pubsub` for real-time fan-out of game state deltas.

---

## 5. Cloudflare R2 (Assets)

### Stack:
- Static delivery (logos, uniforms, fields)
- Zero egress to Cloudflare Pages/Workers

### Setup:
1. Go to R2 in Cloudflare dashboard.
2. Create bucket: `roster-assets`
3. Upload:
   - Field backgrounds
   - Uniform templates
   - Team logos
4. Serve via public link or signed URL.
5. Optionally use Wrangler or s3cmd to upload/update.

---

## 6. Cloudflare DNS

### Stack:
- Full zone management
- TLS via proxy
- Split domain routing

### Setup:
1. Use `rosterpilot.app` as root domain.
2. Create:
   - `app` → Pages domain (CNAME)
   - `api` → Fly IP or Fly hostname (A or CNAME)
3. TLS: Always-on HTTPS, full (strict)
4. Proxy mode: Enabled

---

## 7. Yahoo OAuth Setup

### OAuth Scope: `fspt-r` (read-only)

### Yahoo Dev Console:
1. Register app.
2. Set redirect URI:
   ```
   https://app.rosterpilot.app/oauth/callback
   ```
3. Get:
   - `YAHOO_CLIENT_ID`
   - `YAHOO_CLIENT_SECRET`

### Backend Flow:
- Use OAuth2 code flow.
- Store token encrypted.
- Refresh token periodically.

---

## 8. Environment Variables (Secrets)

Configure in:
- Fly.io for backend
- Cloudflare Pages for frontend

### Backend:
```
DATABASE_URL=
REDIS_URL=
YAHOO_CLIENT_ID=
YAHOO_CLIENT_SECRET=
YAHOO_REDIRECT_URI=https://app.rosterpilot.app/oauth/callback
```

### Frontend:
```
NEXT_PUBLIC_API_URL=https://api.rosterpilot.app
```

---

## 9. Observability (optional)

- Add `/metrics` Prometheus endpoint
- Include:
  - WS fan-out size
  - Upstream Yahoo/PyESPN latency
  - Redis hit/miss
  - DB query time

---

## 10. Cold Start Behavior

- **Neon:** Cold start ~1–3 sec if idle 5+ min
- **Fly.io:** No cold start if 1 VM always on (~$3.60/mo)
- **Upstash:** Near-zero cold latency
- **Cloudflare Pages:** Fully static; no cold latency

---

## Estimated Cost

| Service        | Plan         | Est. Monthly Cost |
|----------------|--------------|-------------------|
| Cloudflare Pages | Free       | $0                |
| Fly.io         | 1 shared-1x VM | ~$3.60          |
| Neon DB        | Free Tier     | $0               |
| Upstash Redis  | Free Tier     | $0               |
| Cloudflare R2  | Free Tier     | $0               |
| **Total**      |               | **~$3.60/mo**     |

---

## Final Notes

- Separate YAML/JSON files define schema mappings from Yahoo and PyESPN to internal DB.
- Game replays and animations require local or CDN fixture JSONs.
- Yahoo token storage must be encrypted.
- Live Game Center requires low-latency WS—confirm Fly WS survives reconnects and reloads.

