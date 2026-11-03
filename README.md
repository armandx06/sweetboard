# SWEETBOARD

Sweetboard is the management platform for **Repostería Cárdenas**. It centralizes the bakery's staff, customers, suppliers, and their shared addresses. The repository is a monorepo with two Next.js applications, a FastAPI service, and a PostgreSQL database running in Docker.

## Stack

| Area          | Technology                                                     |
| ------------- | -------------------------------------------------------------- |
| Landing page  | Next.js 16 (App Router), React 19, Tailwind CSS 4              |
| Web app       | Next.js 16 (App Router), React 19, Tailwind CSS 4              |
| API           | Python 3.13, FastAPI, SQLAlchemy 2.0 (async), asyncpg, Alembic |
| Database      | PostgreSQL 18                                                  |
| Local tooling | Docker Compose, pnpm, uv, ChartDB                              |

## Repository layout

```text
apps/
├── landing/          # Public landing page (port 3000)
├── web/              # Management web app (port 3001)
└── api/              # FastAPI service, models, CRUD, tests, migrations
docs/
├── adr/              # Architecture Decision Records
├── api/              # HTTP API reference
└── db/               # Schema documentation, ChartDB export, DDL snapshot
infra/docker/         # Compose stack (base + development overlay)
```

## Requirements

- Docker Engine with Compose v2
- Node.js 22+ and pnpm 11.20+
- [uv](https://docs.astral.sh/uv/) only if you want to run the API tests or linter locally

The API itself runs inside Docker; a local Python installation is not required to start the stack.

## Setup

1. Clone the repository and enter its root directory.
2. Create the shared environment file:

   ```bash
   cp .env.example .env
   ```

   The root `.env` is read by both Docker Compose and the API. Keep `ALLOWED_ORIGINS` as a JSON array, for example `["http://localhost:3000", "http://localhost:3001"]`.

3. Install the frontend dependencies from the repository root:

   ```bash
   pnpm install
   ```

4. Create the frontend environment files:

   ```bash
   cp apps/landing/.env.example apps/landing/.env.local
   cp apps/web/.env.example apps/web/.env.local
   ```

   Both must contain `NEXT_PUBLIC_API_URL=http://localhost:8000`.

5. Start the infrastructure (database, API, ChartDB, and the test database):

   ```bash
   pnpm dev:infra
   ```

6. Verify that the API can reach the database:

   ```bash
   curl http://localhost:8000/health
   ```

7. Start the frontend you need, in a separate terminal:

   ```bash
   pnpm --filter landing dev   # http://localhost:3000
   pnpm --filter web dev       # http://localhost:3001
   ```

## Services and ports

| Service           | URL / port                     | Notes                                       |
| ----------------- | ------------------------------ | ------------------------------------------- |
| Landing           | <http://localhost:3000>        | Next.js development server                  |
| Web               | <http://localhost:3001>        | Next.js development server                  |
| API               | <http://localhost:8000>        | FastAPI                                     |
| API documentation | <http://localhost:8000/docs>   | Swagger UI; OpenAPI JSON at `/openapi.json` |
| API health        | <http://localhost:8000/health> | Checks the database connection              |
| PostgreSQL        | `localhost:5432`               | Development database                        |
| Test PostgreSQL   | `localhost:5433`               | Used by `uv run pytest`                     |
| ChartDB           | <http://localhost:8080>        | Development-only ER modeling tool           |

Ports and credentials come from the root `.env`; see [`.env.example`](./.env.example) for every variable.

## Common commands

### Infrastructure

| Command                | Description                                                                   |
| ---------------------- | ----------------------------------------------------------------------------- |
| `pnpm dev:infra`       | Start every service in the background                                         |
| `pnpm dev:infra:down`  | Stop the containers and keep the database volumes                             |
| `pnpm dev:infra:reset` | Stop the containers and remove the volumes, wiping the development database   |
| `pnpm dev:infra:logs`  | Follow logs; pass a service name to filter, e.g. `pnpm dev:infra:logs -- api` |
| `pnpm dev:infra:ps`    | Show container status                                                         |

The scripts always merge `infra/docker/docker-compose.yml` with `infra/docker/docker-compose.dev.yml` and use `--project-directory .`, so Compose reads the same root `.env`. The development overlay adds ChartDB and `test_db`.

### Frontend

```bash
pnpm --filter landing dev
pnpm --filter web dev
pnpm --filter landing lint
pnpm --filter web lint
pnpm --filter landing build
pnpm --filter web build
```

There is no separate type-check script; `next build` acts as the type check.

### API tests and lint

The API image is built with `--no-dev`, so pytest is not available inside the container. Run the tests locally from `apps/api`:

```bash
cd apps/api
uv sync
uv run pytest
uv run ruff check app tests
```

The tests require the `test_db` service from `pnpm dev:infra`. See [`apps/api/README.md`](./apps/api/README.md) for the full API workflow.

## Database and migrations

Apply migrations from the repository root:

```bash
docker compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml \
  --project-directory . exec api alembic upgrade head
```

Create a migration after changing the models:

```bash
docker compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml \
  --project-directory . exec api alembic revision --autogenerate -m "description"
```

Verify that the models and the database are in sync:

```bash
docker compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml \
  --project-directory . exec api alembic check
```

Autogenerate only sees models imported in `app/models/__init__.py`; export every new model there. The API source is bind-mounted and reloaded by `fastapi dev`. Rebuild the API image only after dependency changes:

```bash
docker compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml \
  --project-directory . up -d --build api
```

## Documentation

| Document                                       | Contents                                                               |
| ---------------------------------------------- | ---------------------------------------------------------------------- |
| [`docs/README.md`](./docs/README.md)           | Documentation index, maintenance rules, and where to start             |
| [`docs/api/README.md`](./docs/api/README.md)   | HTTP API reference: endpoints, payloads, errors, and address semantics |
| [`docs/db/README.md`](./docs/db/README.md)     | Tables, relationships, constraints, business rules, migration history  |
| [`docs/db/schema.sql`](./docs/db/schema.sql)   | Schema-only PostgreSQL dump of the implemented database                |
| [`docs/db/schema.json`](./docs/db/schema.json) | ChartDB native save/export of the ER model                             |
| [`docs/adr/`](./docs/adr/)                     | Architecture Decision Records and their index                          |
| [`CONTRIBUTING.md`](./CONTRIBUTING.md)         | Branch, commit, verification, migration, and pull request workflow     |

### ChartDB workflow

ChartDB runs only in development at <http://localhost:8080>. Diagrams live in the browser's local storage, so the container does not preserve them. After a schema change:

1. Apply the model and migration changes.
2. Regenerate `docs/db/schema.sql`.
3. Update the diagram in ChartDB.
4. Export it as JSON and overwrite `docs/db/schema.json`.
5. Commit both files with the migration and documentation changes.

Do not hand-edit `schema.json`; it must remain a native ChartDB export. See [`docs/db/README.md`](./docs/db/README.md) for the full procedure and the limits of the ChartDB representation.

---

Made by [armandx06](https://github.com/armandx06) at August 30, 2026. Updated November 3, 2026.
