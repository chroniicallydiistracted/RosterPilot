# Frontend Application

The Next.js frontend delivers the companion experience outlined in
`SCAFFOLD_PHASE_PLAN.md` and the frontend feature overview. It now includes
data-backed dashboard panels, optimizer insights, the live game center, and
roadmap placeholders for waivers and trades—all aligned with the read-only Yahoo
scope and PyESPN provenance rules.

## Directory Highlights

- `app/`
  - `layout.tsx` loads runtime configuration from the backend and wires global
    providers.
  - Route segments for `/dashboard`, `/optimizer`, `/waivers`, `/trade`, and
    `/live` render feature-specific views backed by shared context.
- `components/`
  - `layout/` contains the application shell with navigation, environment badge,
    and league/week selectors.
  - Feature directories (`dashboard/`, `optimizer/`, `live/`, etc.) host the
    React views, styled with CSS modules and provenance-aware badges.
- `hooks/`
  - SWR-based hooks for `/me/leagues`, `/leagues/{league}/roster`, `/games`
    endpoints, and WebSocket deltas.
- `lib/`
  - Runtime configuration + environment helpers, API client utilities, and
    roster math shared across components.
- `tests/`
  - Jest + Testing Library setup with coverage collection for components, hooks,
    and utilities.

## Running Locally

```bash
cd frontend
npm install
npm run dev
```

Ensure the backend is running (or fixtures are available) so `/api/meta/config`
and core endpoints respond. Environment variables are read from
`.env.local` (see `frontend/.env.production.example`).

## Test & Lint

- `npm run lint` – Next.js lint rules.
- `npm run test` – Jest + React Testing Library.

## Feature Surfaces

- **Dashboard** – Live roster overview, optimizer rationale, and provenance
  badges.
- **Optimizer** – Suggested swaps with lock toggles and recommended lineup
  summary.
- **Live Game Center** – Scoreboard, drive timeline, and WebSocket-driven play
  feed with live/replay modes.
- **Waivers & Trade** – Roadmap cards outlining upcoming capabilities, keeping
  the UI aligned with the published plan.

Contributions should preserve provenance indicators, accessibility, and the
performance targets called out in the architecture docs.
