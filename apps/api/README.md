# SWEETBOARD API

Sweetboard's backend, built with FastAPI, SQLAlchemy (async), and PostgreSQL.

## Requirements

- Docker and Docker Compose
- A `.env` file in the repo root (copy from [`.env.example`](../../.env.example))
- [uv](https://docs.astral.sh/uv/) installed locally (optional, only needed for IDE type-checking and dependency resolution outside the container)

## Virtual environment for IDE type-checking and dependency resolution outside the container

From `apps/api/`:

```bash
uv sync
```

This creates the virtual environment and installs the exact dependencies specified in `uv.lock`.

## Running the stack

The API container depends on the database container, both must be running

From the repo root:

```bash
docker compose -f infra/docker/docker-compose.yml --project-directory . up -d --build
```

The API is available at `http://localhost:8000`. Interactive documentation is available at `http://localhost:8000/docs`.

Health check endpoint (confirms an actual connection to the database):

```bash
curl http://localhost:8000/health
```

Code changes under `app/` and `alembic/` are reflected live thanks to the mounted volumes and `fastapi dev`'s reload — no rebuild needed for those changes. Rebuild only when dependencies (`pyproject.toml` / `uv.lock`) change.

## Migrations (Alembic)

All Alembic commands run inside the `api` container:

```bash
docker compose -f infra/docker/docker-compose.yml --project-directory . exec api uv run alembic revision --autogenerate -m "description of the change"
docker compose -f infra/docker/docker-compose.yml --project-directory . exec api uv run alembic upgrade head
docker compose -f infra/docker/docker-compose.yml --project-directory . exec api uv run alembic downgrade -1
```

Connection credentials are read from `Settings` (`app/core/config.py`), the same source used by both the application and Alembic's `env.py`.

## Structure

```text
app/
├── main.py           # FastAPI instance and root endpoints
├── core/
│   └── config.py     # configuration via pydantic-settings
└── db/
    └── session.py     # SQLAlchemy engine and async session
alembic/               # database migrations
```

---

Created by [armandx06](https://github.com/armandx06) on August 2, 2026
