# SWEETBOARD API

Sweetboard's backend: a Python 3.13 **FastAPI** service using **SQLAlchemy 2.0** with the asynchronous **asyncpg** driver, **Alembic** migrations, and PostgreSQL 18.

The API manages employees, customers, suppliers, and their shared addresses. It has no authentication layer yet: every route is public and relies on the development network boundary.

## Requirements

- Docker Engine with Compose v2 (to run the stack)
- [uv](https://docs.astral.sh/uv/) (to run tests and the linter locally)
- A root `.env` file, copied from [`.env.example`](../../.env.example)

## Running the API

From the repository root:

```bash
pnpm dev:infra
```

This starts PostgreSQL, the API, ChartDB, and the test database. The API is available at:

- API: <http://localhost:8000>
- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>
- OpenAPI JSON: <http://localhost:8000/openapi.json>
- Health check: <http://localhost:8000/health>

```bash
curl http://localhost:8000/health
# {"status":"ok","db_result":1}
```

The API container runs `fastapi dev`, and `app/` plus `alembic/` are bind-mounted. Source changes reload automatically; rebuild only after dependency changes:

```bash
docker compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml \
  --project-directory . up -d --build api
```

## Configuration

`app/core/config.py` loads the root `.env` by walking up the directory tree until it finds `pnpm-workspace.yaml`. Compose and the API therefore share one configuration file.

| Variable                        | Purpose                                                        |
| ------------------------------- | -------------------------------------------------------------- |
| `POSTGRES_USER`                 | Development database user                                      |
| `POSTGRES_PASSWORD`             | Development database password                                  |
| `POSTGRES_DB`                   | Development database name                                      |
| `POSTGRES_HOST`                 | Database host; `db` inside Compose, `localhost` for local tests |
| `POSTGRES_INTERNAL_PORT`        | Database port inside the Compose network                       |
| `POSTGRES_TESTDB_USER`          | Test database user                                             |
| `POSTGRES_TESTDB_PASSWORD`      | Test database password                                         |
| `POSTGRES_TESTDB_DB`            | Test database name                                             |
| `POSTGRES_TESTDB_HOST`          | Test database host; `test_db` in Compose, `localhost` in tests |
| `POSTGRES_TESTDB_INTERNAL_PORT` | Test database port used by the tests                           |
| `ALLOWED_ORIGINS`               | CORS origins as a JSON array, e.g. `["http://localhost:3001"]` |

`tests/conftest.py` forces `POSTGRES_HOST` and `POSTGRES_TESTDB_HOST` to `localhost`, and `POSTGRES_TESTDB_INTERNAL_PORT` to `5433`, before importing the application settings. Tests therefore connect to the host-published test database.

## Local environment, tests, and lint

Run these commands from `apps/api`:

```bash
uv sync                      # creates .venv and installs runtime + dev dependencies
uv run pytest                # full test suite
uv run ruff check app tests  # lint
```

Single test:

```bash
uv run pytest tests/test_employees.py::test_create_employee
```

Test requirements and behavior:

- The `test_db` service must be running (`pnpm dev:infra` starts it) on host port `5433`.
- `uv run pytest` must be executed from `apps/api`: pytest uses `pythonpath = ["."]`, tests import `tests.conftest`, and `conftest.py` opens `alembic.ini` relative to the current directory.
- The session-scoped fixture applies `alembic upgrade head` to the test database once per test session.
- The `client` fixture wraps each test in nested transactions and rolls them back.
- The `concurrent_client` fixture commits real rows and truncates every table afterward.
- The API image is built with `--no-dev`, so pytest and ruff are **not** available inside the `api` container. Use the local `uv` environment for both.

## Migrations

Alembic runs inside the `api` container. The final image does not include the `uv` executable, so call `alembic` directly:

```bash
# Apply all pending migrations
docker compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml \
  --project-directory . exec api alembic upgrade head

# Create a migration from the current models
docker compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml \
  --project-directory . exec api alembic revision --autogenerate -m "description"

# Roll back one revision
docker compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml \
  --project-directory . exec api alembic downgrade -1

# Check whether models and the database are in sync
docker compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml \
  --project-directory . exec api alembic check

# Show the current revision
docker compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml \
  --project-directory . exec api alembic current
```

Important details:

- Autogenerate only detects models imported in `app/models/__init__.py`. Export every new model there.
- `alembic/env.py` uses `settings.database_url` unless the `sqlalchemy_url_override` config attribute is set; the tests use that override to target `test_db`.
- Schema changes must be made through Alembic. `docs/db/schema.sql` is a snapshot, not an executable migration source.

## Structure

```text
app/
├── main.py                  # FastAPI instance, CORS, /health, router registration
├── core/
│   ├── config.py            # pydantic-settings; locates the root .env
│   ├── datetime.py          # now() and today() helpers
│   └── security.py          # password generation and bcrypt hashing
├── db/
│   └── session.py           # async engines, session factories, get_db/get_test_db
├── models/
│   ├── base.py              # declarative Base and constraint naming convention
│   ├── mixins.py            # UUIDMixin, TimestampMixin, PersonMixin
│   ├── address.py           # Address + customer/supplier/employee link tables
│   ├── customer.py
│   ├── employee.py
│   └── supplier.py
├── schemas/
│   ├── address.py           # address and link read/create/update bodies
│   ├── customer.py
│   ├── employee.py
│   └── supplier.py
├── crud/
│   ├── customer.py
│   ├── employee.py
│   └── supplier.py
├── routers/
│   ├── customer.py
│   ├── employee.py
│   └── supplier.py
├── exceptions/
│   ├── exceptions.py        # domain exceptions, no HTTP knowledge
│   └── handlers.py          # APIException and IntegrityError handlers
alembic/
├── env.py
└── versions/
tests/
├── conftest.py
├── test_customers.py
├── test_employees.py
└── test_suppliers.py
```

## API conventions

- **Layers:** `app/routers` handles HTTP and response models, `app/crud` contains database/domain logic, and `app/models` plus `app/schemas` define persistence and contracts.
- **Domain exceptions:** CRUD raises `APIException` subclasses from `app/exceptions/exceptions.py`, never `HTTPException`. `app/exceptions/handlers.py` maps them to HTTP responses and maps `IntegrityError` to `409 Conflict`.
- **Async relationships:** `AsyncSession` does not lazy-load. Any relationship used in a response is eager-loaded with `selectinload`/`joinedload` to avoid `MissingGreenlet` (ADR 0002).
- **Shared addresses:** `addresses` has no owner column. Role-specific flags live in `customer_addresses`, `supplier_addresses`, and `employee_addresses` (ADR 0008).
- **Employee identity:** usernames and passwords are server-generated; plaintext passwords appear only in the create and reset-password responses; deactivation is the soft delete (ADR 0007).
- **Schemas:** those decisions are recorded in [`docs/adr/`](../../docs/adr/). Read the relevant ADR before changing schema or domain behavior.

The complete HTTP reference is in [`docs/api/README.md`](../../docs/api/README.md). The live, always-current contract is the OpenAPI document at `/openapi.json`.

---

Created by [armandx06](https://github.com/armandx06) on August 2, 2026. Updated November 3, 2026.
