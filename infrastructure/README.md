# Infrastructure Providers Bootstrap

This directory captures environment-specific provisioning notes and IaC stubs for the
RosterPilot stack providers outlined in `DEPLOYMENT.md`.

## Providers

- **Google Cloud Run** – Containerized FastAPI backend. Requires Docker image built from
  `backend/Dockerfile` and deployed via `gcloud run deploy`.
- **Neon Postgres** – Primary relational datastore. Connection string supplied through the
  `DATABASE_URL` environment variable.
- **Upstash Redis** – Serverless cache and pub/sub provider surfaced through `REDIS_URL`.
- **Cloudflare Pages** – Next.js frontend hosting consuming the backend API + WebSocket endpoints.

## Next Steps

1. Add Terraform or Pulumi modules under `infrastructure/terraform/` or `infrastructure/pulumi/`
   to automate resource provisioning.
2. Define GitHub Actions workflows that build and push the backend container, then trigger Cloud Run
   deployments once secrets are configured.
3. Document secret management conventions (Google Secret Manager, Cloudflare environment secrets)
   and ensure `.env` files are never committed.
4. Capture environment topologies (staging, production) and networking considerations as the stack
   evolves.
