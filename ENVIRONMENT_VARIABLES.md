# ENVIRONMENT_VARIABLES.md — RosterPilot
**Date:** 2025-10-23  
**Stack:** Cloudflare Pages · Google Cloud Run (FastAPI) · Neon Postgres · Upstash Redis

Legend: **Secret** = keep in GCP Secret Manager or CI secrets. **Public** = safe for client or build logs.

---

## A) Global (used across components)
| Name | Example | Purpose | Secret | Set Where |
|---|---|---|---|---|
| `APP_ENV` | `production` | Runtime mode toggle | No | Backend, Frontend build |
| `APP_BASE_URL` | `https://rosterpilot.westfam.media` | Canonical site URL | No | Frontend build |
| `API_BASE_URL` | `https://api.westfam.media` | Base URL for API calls | No | Frontend build, Backend (CORS) |
| `CORS_ALLOWED_ORIGINS` | `https://rosterpilot.westfam.media` | Allowed origin(s) for API | No | Backend |
| `LOG_LEVEL` | `INFO` | Logging verbosity | No | Backend |
| `TZ` | `America/Phoenix` | Consistent timezone | No | Backend |

---

## B) Backend — FastAPI on Cloud Run
| Name | Example | Purpose | Secret | Set Where |
|---|---|---|---|---|
| `PORT` | `8080` | Cloud Run injected port | No | Cloud Run |
| `DATABASE_URL` | `postgres://user:pwd@host/db?sslmode=require` | Primary Neon pooled connection | **Yes** | Secret Manager → env |
| `REDIS_URL` | `rediss://:token@us1-redis.upstash.io:6379` | Upstash Redis connection | **Yes** | Secret Manager → env |
| `YAHOO_CLIENT_ID` | `dj0yJmk9...` | Yahoo OAuth client id | **Yes** | Secret Manager → env |
| `YAHOO_CLIENT_SECRET` | `xxxxxxxx` | Yahoo OAuth client secret | **Yes** | Secret Manager → env |
| `YAHOO_REDIRECT_URI` | `https://api.westfam.media/oauth/callback` | OAuth callback URL | No | Backend env |
| `YAHOO_SCOPE` | `fspt-r` | Read-only fantasy scope | No | Backend env |
| `SESSION_SECRET` | random 32+ chars | Sign server session/JWT | **Yes** | Secret Manager → env |
| `TOKEN_ENC_KEY` | base64 key | Encrypt stored refresh tokens | **Yes** | Secret Manager → env |
| `COOKIE_DOMAIN` | `.westfam.media` | Scope cookies to parent domain | No | Backend env |
| `COOKIE_SECURE` | `true` | Force HTTPS cookies | No | Backend env |
| `RATE_LIMIT_WINDOW` | `60` | Seconds per window | No | Backend env |
| `RATE_LIMIT_MAX` | `120` | Requests per window | No | Backend env |
| `CACHE_TTL_DEFAULT` | `300` | Seconds for generic cache | No | Backend env |
| `WS_HEARTBEAT_SEC` | `25` | Ping interval to keep WS alive | No | Backend env |
| `FEATURE_WEATHER` | `false` | Gate weather features | No | Backend env |
| `FEATURE_REPLAY` | `true` | Enable replay mode | No | Backend env |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `https://otlp.yourvendor.com` | Traces/metrics endpoint | No | Backend env |
| `OTEL_EXPORTER_OTLP_HEADERS` | `api-key=xxxxx` | Auth for OTLP | **Yes** | Secret Manager → env |
| `SENTRY_DSN` | `https://...ingest.sentry.io/...` | Error reporting | **Yes** | Secret Manager → env |

> Store all **secrets** in Google Secret Manager and mount with `--set-secrets` on `gcloud run deploy`.

---

## C) Frontend — Next.js on Cloudflare Pages
| Name | Example | Purpose | Secret | Set Where |
|---|---|---|---|---|
| `NEXT_PUBLIC_API_URL` | `https://api.westfam.media` | API base used by browser | No (public) | Pages → Project env |
| `NEXT_PUBLIC_WS_URL` | `wss://api.westfam.media/ws` | WebSocket endpoint | No (public) | Pages → Project env |
| `NEXT_PUBLIC_ENV` | `production` | Client-side feature flags/gates | No (public) | Pages env |

> Do **not** expose server secrets in Pages. Only `NEXT_PUBLIC_*` vars are read by the client bundle.

---

## D) Neon — Postgres
| Name | Example | Purpose | Secret | Set Where |
|---|---|---|---|---|
| `DATABASE_URL` | `postgres://...neon.tech/...` | Pooled connection (pgBouncer) | **Yes** | Secret Manager |
| `DB_POOL_MAX` | `10` | App-level pool size | No | Backend env |
| `ALEMBIC_CONFIG` | `alembic.ini` | Migrations config path | No | Backend |
| `NEON_BRANCH` | `prod` | Optional: branch name | No | Backend |

> Prefer Neon’s pooled URL. Use `sslmode=require`.

---

## E) Upstash — Redis
| Name | Example | Purpose | Secret | Set Where |
|---|---|---|---|---|
| `REDIS_URL` | `rediss://:token@host:port` | Redis over TLS | **Yes** | Secret Manager |
| `UPSTASH_REST_URL` | `https://...upstash.io` | REST API alt endpoint | **Yes** | Secret Manager |
| `UPSTASH_REST_TOKEN` | `xxxxxxxx` | REST API auth | **Yes** | Secret Manager |
| `REDIS_NAMESPACE` | `rp:` | Key prefix | No | Backend |

---

## F) OAuth (Yahoo) — server-side Authorization Code
| Name | Example | Purpose | Secret | Set Where |
|---|---|---|---|---|
| `YAHOO_CLIENT_ID` | `dj0yJmk9...` | Issued by Yahoo | **Yes** | Secret Manager |
| `YAHOO_CLIENT_SECRET` | `xxxxxxxx` | Issued by Yahoo | **Yes** | Secret Manager |
| `YAHOO_REDIRECT_URI` | `https://api.westfam.media/oauth/callback` | Exact match in Yahoo app | No | Backend |
| `YAHOO_SCOPE` | `fspt-r` | Read-only fantasy | No | Backend |
| `OAUTH_STATE_TTL` | `600` | Seconds to accept callback | No | Backend |
| `OAUTH_STATE_SECRET` | random 32+ chars | HMAC state param | **Yes** | Secret Manager |

---

## G) CI/CD (GitHub Actions)
| Name | Example | Purpose | Secret | Set Where |
|---|---|---|---|---|
| `GCP_PROJECT` | `westfam-prod` | Cloud Run project id | No | GitHub Actions secrets |
| `GCP_SA_KEY_JSON` | JSON blob | Deploy auth for GCP | **Yes** | GitHub Actions secrets |
| `CF_API_TOKEN` | token | Cloudflare Pages deploy | **Yes** | GitHub Actions secrets |
| `CF_ACCOUNT_ID` | `xxxxxxxx` | Cloudflare account | **Yes** | GitHub Actions secrets |
| `RP_DATABASE_URL` | same as `DATABASE_URL` | Reference for `--set-secrets` | **Yes** | GitHub Actions secrets |
| `RP_REDIS_URL` | same as `REDIS_URL` | Reference for `--set-secrets` | **Yes** | GitHub Actions secrets |
| `RP_YH_ID` | client id | Reference secret | **Yes** | GitHub Actions secrets |
| `RP_YH_SECRET` | client secret | Reference secret | **Yes** | GitHub Actions secrets |
| `RP_YH_REDIRECT` | redirect uri | Reference secret | **Yes** | GitHub Actions secrets |

---

## H) Optional (use if enabled)
| Name | Example | Purpose | Secret | Set Where |
|---|---|---|---|---|
| `S3_BUCKET_ASSETS` | `rosterpilot-assets` | If using R2/S3 for images | No | Backend/Build |
| `ASSETS_BASE_URL` | `https://static.westfam.media` | CDN origin for assets | No | Frontend |
| `PYESPN_SEASON_YEAR` | `2025` | Default season for ingest | No | Backend |
| `PYESPN_POLL_MS` | `2000` | Live poll interval | No | Backend |
| `ADMIN_EMAILS` | `andy@westfam.media` | Admin gates | No | Backend |
| `MAINTENANCE_MODE` | `false` | Read-only switch | No | Backend |

---

## I) `.env` templates

**backend/.env.example**
```
APP_ENV=production
LOG_LEVEL=INFO
TZ=America/Phoenix

DATABASE_URL=postgres://user:pwd@host/db?sslmode=require
REDIS_URL=rediss://:token@host:6379

YAHOO_CLIENT_ID=
YAHOO_CLIENT_SECRET=
YAHOO_REDIRECT_URI=https://api.westfam.media/oauth/callback
YAHOO_SCOPE=fspt-r

SESSION_SECRET=
TOKEN_ENC_KEY=
COOKIE_DOMAIN=.westfam.media
COOKIE_SECURE=true

CORS_ALLOWED_ORIGINS=https://rosterpilot.westfam.media
CACHE_TTL_DEFAULT=300
WS_HEARTBEAT_SEC=25

FEATURE_WEATHER=false
FEATURE_REPLAY=true

OTEL_EXPORTER_OTLP_ENDPOINT=
OTEL_EXPORTER_OTLP_HEADERS=
SENTRY_DSN=
```

**frontend/.env.production.example**
```
NEXT_PUBLIC_API_URL=https://api.westfam.media
NEXT_PUBLIC_WS_URL=wss://api.westfam.media/ws
NEXT_PUBLIC_ENV=production
```
