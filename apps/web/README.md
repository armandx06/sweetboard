# SWEETBOARD WEB

Management web application for Sweetboard. It is a Next.js 16 App Router project using React 19, the React Compiler, and Tailwind CSS 4.

The current UI is intentionally minimal: `/` links to `/health`, and `/health` calls `GET /health` on the API and displays the result. Feature screens will be added incrementally.

## Requirements

- Node.js 22+
- pnpm 11.20+
- The API running at `http://localhost:8000` (start it with `pnpm dev:infra` from the repository root)
- A local `.env.local`

## Setup

Run these commands from the repository root; installing inside `apps/web` targets a different pnpm workspace:

```bash
pnpm install
cp apps/web/.env.example apps/web/.env.local
pnpm dev:infra
pnpm --filter web dev
```

The app is available at <http://localhost:3001>.

`apps/web/.env.local` must contain:

```dotenv
NEXT_PUBLIC_API_URL=http://localhost:8000
```

`NEXT_PUBLIC_API_URL` is inlined into the client bundle when the dev server starts. Restart `pnpm --filter web dev` after changing it.

## Scripts

| Command                   | Description                                   |
| ------------------------- | --------------------------------------------- |
| `pnpm --filter web dev`   | Start the development server on port `3001`   |
| `pnpm --filter web build` | Production build; also acts as the type check |
| `pnpm --filter web start` | Serve the production build                    |
| `pnpm --filter web lint`  | Run ESLint 9 with the Next.js flat config     |

There is no separate type-check script.

## Structure

```text
src/
└── app/
    ├── layout.tsx       # Root layout, fonts, metadata
    ├── page.tsx         # Home page; links to /health
    ├── globals.css      # Tailwind entry point
    └── health/
        └── page.tsx     # Client page that calls the API health endpoint
```

- Path alias `@/*` maps to `./src/*`.
- React Compiler is enabled in `next.config.ts`; do not add manual memoization by default.
- Tailwind CSS 4 is configured through `@tailwindcss/postcss`.
- There is no shared UI package; components live inside each app.

## Verification

From the repository root:

```bash
pnpm --filter web lint
pnpm --filter web build
```

To verify the health page end to end, start the API and the app, then open <http://localhost:3001/health>.

## Related documentation

- [Root README](../../README.md): full stack setup and services.
- [API reference](../../docs/api/README.md): endpoints and payloads.
- [Contributing](../../CONTRIBUTING.md): branch, commit, and verification workflow.

---

Made by [armandx06](https://github.com/armandx06) at August 5, 2026. Updated November 3, 2026.
