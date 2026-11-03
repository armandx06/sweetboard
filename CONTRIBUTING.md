# CONTRIBUTING

This repository is a pnpm monorepo with two Next.js apps, a FastAPI service, and a PostgreSQL development stack. This guide covers the workflow that is not automated: there is no CI, pre-commit hook, or root test script, so verification is manual.

## Before you start

Read these in order:

1. [README.md](./README.md) for the full-stack setup.
2. [docs/README.md](./docs/README.md) for the documentation map.
3. [AGENTS.md](./AGENTS.md) if you are working with an AI coding agent.
4. The relevant [ADR](./docs/adr/README.md) before changing schema or domain behavior.

## First-time setup

From the repository root:

```bash
cp .env.example .env
pnpm install
cp apps/landing/.env.example apps/landing/.env.local
cp apps/web/.env.example apps/web/.env.local
pnpm dev:infra
curl http://localhost:8000/health
```

Keep `ALLOWED_ORIGINS` in `.env` as a JSON array:

```dotenv
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:3001"]
```

The root `.env` is shared by Docker Compose and the API. Do not install from inside `apps/web` or `apps/landing`; run pnpm commands from the repository root.

## Branches

- `develop` is the active integration branch.
- `main` is the other long-lived branch.
- Create a focused topic branch from `develop` and target `develop` with your pull request unless the change is a release or hotfix intended for `main`.

Keep unrelated changes in separate branches. In particular, do not mix a schema migration, a frontend change, and a documentation rewrite in one pull request unless they are part of the same decision.

## Commit messages

Use Conventional Commits with an area scope:

```text
feat(address): add shared address lifecycle
fix(employee_address): clear default flag on unlink
docs(api): document supplier RFC validation
test(customer_address): cover default replacement
chore(infra): add test database service
```

Common scopes in this repository: `address`, `customer`, `customer_address`, `employee`, `employee_address`, `supplier`, `supplier_address`, `api`, `db`, `docs`, `infra`, `web`, `landing`.

Use the imperative mood and explain the behavior change, not the file list. If a commit includes a migration, mention it in the body.

## Verification

Run the checks that match your change. There is no CI to do it for you.

### API

From `apps/api`:

```bash
uv sync
uv run ruff check app tests
uv run pytest
```

Single test:

```bash
uv run pytest tests/test_employees.py::test_create_employee
```

Tests require the `test_db` service on host port `5433`, started by `pnpm dev:infra`. The API container is built with `--no-dev`, so run pytest and ruff locally, not with `docker compose exec`.

### Frontend

From the repository root:

```bash
pnpm --filter landing lint
pnpm --filter web lint
pnpm --filter landing build
pnpm --filter web build
```

There is no separate type-check script; `next build` performs the type check.

### Database and schema

From the repository root:

```bash
docker compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml \
  --project-directory . exec api alembic check
```

If you changed the schema, also:

1. Create and apply an Alembic migration.
2. Regenerate `docs/db/schema.sql` with the command in its header.
3. Update the ChartDB diagram and export `docs/db/schema.json`.
4. Update `docs/db/README.md` with the new tables, constraints, and business rules.

Do not hand-edit `docs/db/schema.json`; it is a native ChartDB export, only minify the JSON file.

### Documentation

Check that relative links resolve and that commands state their working directory. If the change affects setup, ports, scripts, tests, or migrations, update the relevant README as part of the same change.

## Database changes

Schema changes follow [ADR 0005](./docs/adr/0005-single-source-of-truth-for-database-schema-documentation.md) and [ADR 0006](./docs/adr/0006-incremental-table-by-table-modeling-instead-of-full-upfront-er-design.md):

- Model the table group in ChartDB, then implement it; do not model the entire remaining domain up front.
- Create the SQLAlchemy model and export it from `app/models/__init__.py` so autogenerate can see it.
- Generate the migration with Alembic; review the generated file before applying it.
- Add tests for the new behavior, including constraints and lifecycle rules.
- Update `docs/db/README.md`, `docs/db/schema.sql`, and `docs/db/schema.json`.
- Run `alembic check` and confirm it reports no new upgrade operations.

Schema changes must go through Alembic. `docs/db/schema.sql` is a snapshot, not an executable migration source.

## API changes

Follow the layering described in the ADRs:

- `app/routers`: HTTP concerns and response models.
- `app/crud`: database and domain logic.
- `app/models`: SQLAlchemy persistence.
- `app/schemas`: request/response contracts.

Rules that are easy to break:

- CRUD raises domain exceptions from `app/exceptions/exceptions.py`, never `HTTPException`.
- `AsyncSession` does not lazy-load; eager-load every relationship used in a response.
- Cross-model relationships use string forward references to avoid circular imports.
- Addresses are shared; role-specific flags belong in the link tables, not in `addresses`.
- Employee usernames and passwords are server-generated; plaintext passwords appear only in create and reset-password responses.
- Employee deactivation is the soft delete. Hard `DELETE` is intended only for records that were never hired, but the guard is not implemented yet, as noted in [ADR 0007](./docs/adr/0007-employee-identity-credentials-and-lifecycle.md).

When you add or change a route, update [`docs/api/README.md`](./docs/api/README.md) and its tests.

## Pull requests

There is no pull request template or automated gate. Include:

- A short summary of the behavior change and the reason for it.
- The verification commands you ran and their results.
- Any migration, environment variable, port, or dependency change.
- Screenshots or a short description for visible frontend changes.
- Known limitations or follow-up work.

If a check could not be run, say so explicitly instead of leaving it implied.

## Documentation changes

Use the index at [docs/README.md](./docs/README.md). In short:

- API reference: `docs/api/README.md`.
- Database reference: `docs/db/README.md`.
- Decisions: a new or amended ADR under `docs/adr/`; start from `docs/adr/template.md`.
- Workflow and setup: this file and the root README.

Keep documentation in English, use relative links, and avoid duplicating volatile values such as the current Alembic head in multiple documents.

---

Made by [armandx06](https://github.com/armandx06) at November 3, 2026.
