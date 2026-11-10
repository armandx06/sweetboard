# AGENTS.md

## Repo shape

- pnpm workspace with two independent Next.js apps: `apps/landing` (port 3000) and `apps/web` (port 3001). Run pnpm from the repo root (`pnpm --filter web dev`); `apps/*` also contain their own `pnpm-workspace.yaml`/lockfiles, so installing from inside an app targets a different workspace.
- `apps/api` is a Python 3.13 FastAPI + async SQLAlchemy service managed with `uv`; it is not a pnpm package.
- `infra/docker/` holds the Compose stack. The root `.env` is shared by Compose and the API; `app/core/config.py` finds it by walking up to `pnpm-workspace.yaml`.
- No CI, pre-commit, or root lint/test scripts exist. Verification is manual.

## Setup and dev

- Copy `.env.example` to `.env`. `ALLOWED_ORIGINS` must stay a JSON array (`["http://..."]`), not comma-separated.
- `pnpm dev:infra` starts db, api, ChartDB, and `test_db` (the dev overlay is required for `test_db`). `pnpm dev:infra:down` keeps data; `pnpm dev:infra:reset` wipes the DB volume.
- API: <http://localhost:8000>, docs at `/docs`, health at `/health`. Web: 3001. Landing: 3000.
- Verify the stack after startup with `curl http://localhost:8000/health`.
- Web/landing each need their own `apps/<app>/.env.local` with `NEXT_PUBLIC_API_URL=http://localhost:8000`.
- API source (`app/`, `alembic/`) is bind-mounted and reloaded by `fastapi dev`. Rebuild only after dependency changes: `docker compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml --project-directory . up -d --build api`.
- ChartDB (<http://localhost:8080>) is dev-only and keeps diagrams in browser localStorage; export schema snapshots to `docs/db/`.

## API workflow

- From `apps/api`: `uv sync` (installs the dev group), `uv run pytest`, `uv run ruff check`.
- Single test: `uv run pytest tests/test_employees.py::test_create_employee`.
- Tests must run from `apps/api`: pytest uses `pythonpath = ["."]`, tests import `tests.conftest`, and `conftest.py` opens `alembic.ini` relative to the cwd.
- The api image is built with `--no-dev`, so pytest is not available inside the container. Run tests locally with `uv`.
- Tests need the `test_db` service (host port 5433). `tests/conftest.py` forces `POSTGRES_HOST`/`POSTGRES_TESTDB_HOST` to `localhost` and runs `alembic upgrade head` against the test DB once per session.
- Test fixtures: `client` rolls back each test via nested transactions; `concurrent_client` commits real rows and truncates all tables afterward.
- Migrations (from repo root, matching `apps/api/README.md`):
  - `docker compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml --project-directory . exec api alembic revision --autogenerate -m "description"`
  - `... exec api alembic upgrade head`
  - The final API image does not include `uv`; do not prefix Alembic commands with `uv run` inside the container.
- Autogenerate only sees models imported in `app/models/__init__.py`; export every new model there. `alembic/env.py` uses `settings.database_url` unless the `sqlalchemy_url_override` config attribute is set (tests use this).
- `app/db/session.py` sets `echo=True` on both engines, so SQL logging is intentionally noisy in dev.

## API conventions (from ADRs)

- Layers: `app/routers` (HTTP + response models) -> `app/crud` (DB/domain logic) -> `app/models` / `app/schemas`. CRUD raises domain exceptions from `app/exceptions/exceptions.py`, never `HTTPException`; `app/exceptions/handlers.py` maps them (and `IntegrityError` to 409).
- `AsyncSession` does not lazy-load relationships (ADR 0002). Eager-load any relationship used in a response with `selectinload`/`joinedload`; otherwise serialization raises `MissingGreenlet`.
- Models inherit `app.models.base.Base` (constraint naming convention) plus `UUIDMixin`/`TimestampMixin`/`PersonMixin`; use `Mapped`/`mapped_column`. Because `app/models/__init__.py` eagerly imports every model (and Alembic imports it), runtime imports between model modules create circular imports; use string forward references (`Mapped["X"]`) for cross-model relationships.
- Addresses are shared: `addresses` has no owner column; per-role link tables (`customer_addresses`, `supplier_addresses`, `employee_addresses`) hold role flags and a partial unique index enforcing one default per subject (ADR 0008). Do not add owner columns to `addresses`.
- Employee rules are deliberate (ADR 0007): usernames/passwords are server-generated, plaintext passwords appear only in create/reset responses, `PATCH` is limited to contact fields, and deactivation is the soft delete. Hard `DELETE` is intended only for never-hired records, but that guard is not implemented yet.

## Documentation

- `docs/db/README.md`, `docs/db/schema.sql`, and `docs/db/schema.json` document the implemented schema. `schema.sql` is a `pg_dump --schema-only` snapshot, and `schema.json` is a native ChartDB export that must not be hand-edited. ChartDB may omit partial unique indexes and `CHECK` constraints; the README and `schema.sql` are authoritative for those. Document only implemented and tested tables (ADR 0005, ADR 0006).
- `docs/api/README.md` is the HTTP reference; update it when routes, payloads, status codes, or error behavior change.
- `docs/design/` holds plans that are not implemented. Do not treat planned tables, endpoints, or rules as current behavior.
- Architectural decisions live in `docs/adr/` (index and template included); read the relevant ADR before changing schema or domain behavior.
- `docs/README.md` is the documentation index. `CONTRIBUTING.md` covers branching, commits, verification, migrations, and pull requests.

## Frontend notes

- Both apps are Next 16 App Router / React 19 with React Compiler enabled (`reactCompiler: true`) and Tailwind v4 via `@tailwindcss/postcss`. There is no shared UI package.
- Lint with `pnpm --filter web lint` / `pnpm --filter landing lint` (flat config, ESLint 9; no `next lint` step). There is no separate typecheck script, so `next build` doubles as the type check.
- `NEXT_PUBLIC_API_URL` (from `apps/<app>/.env.local`) is inlined into the client bundle at dev-server start; changing it requires restarting the Next dev server.
- Path alias `@/*` maps to `./src/*` in each app.

## Git

- Commit messages follow Conventional Commits with an area scope, e.g. `feat(address): ...`, `fix(employee_address): ...`.
- Active development is on `develop`; `main` is the other long-lived branch.
