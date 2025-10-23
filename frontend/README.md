# Frontend Scaffold

The `frontend/` directory houses the Next.js application for the RosterPilot dashboard,
optimizer, and live game center. This initial scaffold provides a TypeScript-ready layout
with placeholders for shared components, hooks, styles, and tests.

## Layout

- `app/` – App Router entrypoints (`layout.tsx`, `page.tsx`) using React Server Components.
- `components/` – Reusable UI components (cards, tables, provenance badges, PixiJS canvas wrappers).
- `hooks/` – Client-side data fetching hooks (SWR/React Query) and WebSocket helpers.
- `lib/` – API client utilities, Yahoo OAuth helpers, formatting functions.
- `styles/` – Global styles, design tokens, Tailwind or CSS modules.
- `tests/` – Jest + Testing Library unit tests (Playwright/Cypress to follow later phases).

## Next Steps

1. Initialize the Next.js project with `next`, `react`, and `react-dom` dependencies.
2. Configure ESLint, Prettier, Tailwind (if selected), and CI workflows.
3. Implement OAuth callback page and API client wrappers using the backend `/auth/yahoo` endpoints.
4. Build foundational UI shells for Dashboard, Optimizer, Waivers, Trade, and Live Game Center views.
5. Add storybook or visual regression suite for critical components.
