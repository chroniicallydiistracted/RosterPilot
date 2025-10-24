# DEPLOYMENT.md — RosterPilot Production Stack

**Date:** 2025-10-23  
**Stack:** Cloudflare Pages (Next.js) · Google Cloud Run (FastAPI + WebSockets) · Neon Postgres · Upstash Redis  
**Audience:** Advanced Coding AI Agent

---

## 0) Architecture and domains

- **Frontend:** Next.js static site on **Cloudflare Pages** → `https://app.rosterpilot.com`
- **Backend:** FastAPI + Uvicorn on **Google Cloud Run** with **WebSockets** → `https://api.rosterpilot.com`
- **DB:** **Neon Postgres** (serverless, auto‑suspend)
- **Cache/PubSub:** **Upstash Redis** (serverless)
- **DNS:** Cloudflare DNS for `rosterpilot.com` (Apex), `app.` and `api.` subdomains
- **TLS:** Managed certs everywhere. All traffic over HTTPS/WSS.

**CORS policy:** Allow origin `https://app.rosterpilot.com` only.  
**Provenance:** Yahoo = fantasy; PyESPN = official NFL. Read‑only OAuth scope for Yahoo (`fspt-r`).

---

## 1) Environment matrix

### Frontend (Cloudflare Pages)
- `NEXT_PUBLIC_API_URL` = `https://api.rosterpilot.com`
- `NEXT_PUBLIC_WS_URL`  = `wss://api.rosterpilot.com/ws`  (match your WS route)

### Backend (Cloud Run)
- `DATABASE_URL` = Neon pooled URL, e.g. `postgres://USER:PWD@HOST/db?sslmode=require`
- `REDIS_URL`    = Upstash `rediss://...` URL
- `YAHOO_CLIENT_ID`
- `YAHOO_CLIENT_SECRET`
- `YAHOO_REDIRECT_URI` = `https://app.rosterpilot.com/oauth/callback`
- Optional feature flags: `FEATURE_WEATHER=false`, `FEATURE_REPLAY=true`

Store backend secrets in **GCP Secret Manager** and mount as env vars at deploy time.

---

## 2) Cloudflare Pages — Next.js frontend

**Goal:** Fully static Next.js build served from the edge.

### Project setup
1. In Next.js, ensure SSG for pages. If you use `next export`, set output to `out/`.
2. Add `.env.production` with the two `NEXT_PUBLIC_*` vars.
3. Commit and push to GitHub.

### Pages configuration
- Create a new Pages project → connect GitHub repo.
- **Build command:** one of
  - `npm ci && npm run build --workspace frontend` (regular static SSG)
  - `npm ci && npm run build --workspace frontend && npm run export --workspace frontend` (if using `next export`)
- **Build output directory:** `.next` (SSG) or `out` (export)
- **Environment variables (Production):** `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_WS_URL`
- **Custom domain:** map `app.rosterpilot.com` to the Pages project.
- **Caching:** place long‑lived assets under `public/` with hashed filenames. Optionally add `_headers` to tune cache.

> SPA fallback: if using client‑side routing only, add `_redirects` with `/*   /index.html   200`

---

## 3) Google Cloud Run — FastAPI + WS backend

**Goal:** Containerized FastAPI with native WebSockets. Scale‑to‑zero when idle.

### Minimal Dockerfile
```dockerfile
# backend/Dockerfile
# syntax=docker/dockerfile:1.6

FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_NO_INTERACTION=1

WORKDIR /app
RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"
COPY pyproject.toml poetry.lock ./
RUN poetry export --without-hashes --format=requirements.txt --output requirements.txt --only main

FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONFAULTHANDLER=1

WORKDIR /app
COPY --from=builder /app/requirements.txt ./
RUN python -m pip install --no-cache-dir "pip==24.2" \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -f requirements.txt

COPY . /app

ENV PORT=8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]
```

> If not using Poetry, replace with `pip install -r requirements.txt`.

### Health endpoints
- `/healthz` returns 200 for liveness/readiness.
- `/ws` for WebSocket upgrades (example route).

### Build and deploy
```bash
# Auth and project
gcloud auth login
gcloud config set project YOUR_GCP_PROJECT
gcloud config set run/region us-central1   # pick closest region

# Build container
gcloud builds submit --tag gcr.io/$GOOGLE_CLOUD_PROJECT/rosterpilot-api:$(git rev-parse --short HEAD)

# Create secrets (one-time)
gcloud secrets create RP_DATABASE_URL --data-file=- <<< "$DATABASE_URL"
gcloud secrets create RP_REDIS_URL    --data-file=- <<< "$REDIS_URL"
gcloud secrets create RP_YH_ID        --data-file=- <<< "$YAHOO_CLIENT_ID"
gcloud secrets create RP_YH_SECRET    --data-file=- <<< "$YAHOO_CLIENT_SECRET"
gcloud secrets create RP_YH_REDIRECT  --data-file=- <<< "$YAHOO_REDIRECT_URI"

# Deploy
gcloud run deploy rosterpilot-api \
  --image gcr.io/$GOOGLE_CLOUD_PROJECT/rosterpilot-api:$(git rev-parse --short HEAD) \
  --platform managed \
  --port 8080 \
  --allow-unauthenticated \
  --concurrency 80 \
  --cpu 1 --memory 512Mi \
  --timeout 3600 \  # keep WS up to 60 min
  --min-instances 0 --max-instances 2 \
  --set-secrets=DATABASE_URL=RP_DATABASE_URL:latest,REDIS_URL=RP_REDIS_URL:latest, \
YAHOO_CLIENT_ID=RP_YH_ID:latest,YAHOO_CLIENT_SECRET=RP_YH_SECRET:latest,YAHOO_REDIRECT_URI=RP_YH_REDIRECT:latest
```

**HTTP/2 + WS:** Cloud Run supports WS; `--timeout 3600` preserves long sessions.  
**CORS:** set `Access-Control-Allow-Origin: https://app.rosterpilot.com` in FastAPI middleware.

### Custom domain for API
```bash
# Map api.rosterpilot.com to the Cloud Run service
gcloud run domain-mappings create \
  --service rosterpilot-api \
  --domain api.rosterpilot.com
```
Add/verify DNS records in Cloudflare as instructed by GCP (A/AAAA to Google endpoints).

### Revisions and rollback
- Each deploy creates a **revision**. Use `gcloud run services describe` and `gcloud run services update-traffic` to roll back.

---

## 4) Neon Postgres — serverless DB

### Create and configure
1. Create a Neon project → default branch (e.g., `main`) and database (e.g., `rp_prod`).
2. Enable **connection pooling** (pgBouncer). Copy pooled connection string.
3. Create a dedicated role for the app with least privilege.
4. Set **`sslmode=require`** in the URL.

### Migrations (Alembic)
```bash
# Example
alembic upgrade head
# or automate on startup:
python -m app.db.run_migrations
```

### Branching
- For staging, create a Neon **branch** (isolated data + its own pooled URL).
- Use separate `DATABASE_URL` per environment.

### Backups
- Enable PITR. Take periodic logical dumps for off‑platform backups.

---

## 5) Upstash Redis — cache & pub/sub

### Create database
1. In Upstash console → Create Redis DB near your Cloud Run region.
2. Copy **`rediss://`** URL and token.

### Python usage
```python
import asyncio, json, os
import redis.asyncio as redis

r = redis.from_url(os.environ["REDIS_URL"], decode_responses=True)

# Cache
await r.setex("proj:lineup:TEAMKEY:WEEK", 300, json.dumps(payload))

# Pub/Sub
pub = r.pubsub()
await pub.subscribe("game:EVENT_ID")
await r.publish("game:EVENT_ID", json.dumps({"type": "score", "home": 7, "away": 0}))

async for msg in pub.listen():
    if msg["type"] == "message":
        data = json.loads(msg["data"])
        # forward to client websockets
```

### Notes
- Keep keys small; use TTLs.
- PUB/SUB fan‑out is optional if a single instance handles all WS clients.

---

## 6) DNS on Cloudflare

- Add root zone `rosterpilot.com` to Cloudflare.
- **app** → CNAME to Cloudflare Pages hostname.
- **api** → follow GCP domain‑mapping instructions (A/AAAA). Keep **proxy ON** only if GCP mapping allows; otherwise **DNS only**.
- Enforce **Always Use HTTPS** and **HSTS** (preload optional).

---

## 7) CI/CD (optional but recommended)

### Backend: GitHub Actions → Cloud Run
```yaml
# .github/workflows/deploy-backend.yml
name: Deploy Backend
on: { push: { branches: [ main ], paths: [ "backend/**" ] } }
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: google-github-actions/setup-gcloud@v2
        with:
          project_id: ${{ secrets.GCP_PROJECT }}
          service_account_key: ${{ secrets.GCP_SA_KEY_JSON }}
      - run: gcloud builds submit --tag gcr.io/${{ secrets.GCP_PROJECT }}/rosterpilot-api:${{ github.sha }}
      - run: |
          gcloud run deploy rosterpilot-api \
            --image gcr.io/${{ secrets.GCP_PROJECT }}/rosterpilot-api:${{ github.sha }} \
            --platform managed --region us-central1 \
            --allow-unauthenticated --port 8080 \
            --concurrency 80 --cpu 1 --memory 512Mi --timeout 3600 \
            --min-instances 0 --max-instances 2 \
            --set-secrets=DATABASE_URL=RP_DATABASE_URL:latest,REDIS_URL=RP_REDIS_URL:latest, \
YAHOO_CLIENT_ID=RP_YH_ID:latest,YAHOO_CLIENT_SECRET=RP_YH_SECRET:latest,YAHOO_REDIRECT_URI=RP_YH_REDIRECT:latest
```

### Frontend: GitHub Actions → Cloudflare Pages
```yaml
# .github/workflows/deploy-frontend.yml
name: Deploy Frontend
on: { push: { branches: [ main ], paths: [ "frontend/**" ] } }
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: |
          cd frontend
          npm ci
          npm run build
      - name: Publish to Cloudflare Pages
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CF_API_TOKEN }}
          accountId: ${{ secrets.CF_ACCOUNT_ID }}
          projectName: rosterpilot
          directory: frontend/.next  # or frontend/out if using next export
          gitHubToken: ${{ secrets.GITHUB_TOKEN }}
        env:
          NEXT_PUBLIC_API_URL: https://api.rosterpilot.com
          NEXT_PUBLIC_WS_URL: wss://api.rosterpilot.com/ws
```

---

## 8) App concerns

- **CORS & Cookies:** Prefer token auth in headers. If cookies used, set `SameSite=None; Secure` and restrict domain.
- **Security:** Never log tokens or PII. Rate‑limit sensitive endpoints. Validate Yahoo OAuth state/nonce.
- **Observability:**  
  - Cloud Run logs + metrics: latency, 5xx rate, WS connections.  
  - Neon: query latency, connection count.  
  - Upstash: monthly commands, errors.  
  - Frontend: basic web vitals.
- **Cold starts:** First hit after idle → small latency on Cloud Run + Neon wake. Acceptable for 1–8 users.
- **Staging:** `stg.app.rosterpilot.com`, `stg.api.rosterpilot.com`, separate Neon branch + Upstash DB.
- **Rollbacks:** Cloud Run revisions; Pages keeps previous deployments; Neon branches for data safety.

---

## 9) Smoke test checklist

1. Pages deploy succeeds; `app.rosterpilot.com` resolves and loads.
2. Cloud Run responds `200 /healthz` and upgrades `GET /ws` to WebSocket.
3. OAuth flow: Yahoo redirect to `.../oauth/callback` works; tokens stored securely.
4. DB: Alembic migrations applied; read/write verified.
5. Redis: `SET`/`GET` and `PUBLISH`/`SUBSCRIBE` verified.
6. Frontend calls REST and opens WSS from a mobile network successfully.
7. Provenance badges: Yahoo vs PyESPN visible for data elements.

---

## 10) Cost notes (typical month, 1–8 users)

- Cloudflare Pages: $0 (static, unlimited)
- Cloud Run: $0 within free tier (scale‑to‑zero). Occasional pennies if you exceed free.
- Neon: $0 within free tier (0.5 GB, 100 CU‑h; auto‑suspend after 5 min idle).
- Upstash: $0 within free tier (≤ 500k commands/month).

---

## 11) `.env` templates

**backend/.env**
```
DATABASE_URL=postgres://USER:PWD@HOST/db?sslmode=require
REDIS_URL=rediss://:TOKEN@HOST:PORT
YAHOO_CLIENT_ID=
YAHOO_CLIENT_SECRET=
YAHOO_REDIRECT_URI=https://app.rosterpilot.com/oauth/callback
FEATURE_WEATHER=false
FEATURE_REPLAY=true
```

**frontend/.env.production**
```
NEXT_PUBLIC_API_URL=https://api.rosterpilot.com
NEXT_PUBLIC_WS_URL=wss://api.rosterpilot.com/ws
```

---

## 12) Notes on WebSockets in FastAPI

- Use a single `/ws` endpoint and route by `event_id` inside the message payload or querystring.
- Keep per‑connection state minimal; broadcast via Upstash PUB/SUB if multiple instances appear.
- Send small deltas, not full game state; include a `sequence` to apply idempotently on the client.

---

## 13) Recommended deploy order

1. **Neon**: create DB + pooled URL; run migrations.  
2. **Upstash**: create DB; store REDIS_URL.  
3. **Cloud Run**: deploy backend with secrets; verify `/healthz`.  
4. **Cloudflare Pages**: deploy frontend; map `app.` domain.  
5. **DNS**: finalize `api.` domain mapping; verify WSS from the app.  

Done.
