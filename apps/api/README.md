# SWEETBOARD API

Sweetboard's backend, built with FastAPI, SQLAlchemy (async), and PostgreSQL.

## Requirements

- [uv](https://docs.astral.sh/uv/) installed
- Docker and Docker Compose (to run PostgreSQL; [see `README.md` in the repo root](../../README.md))
- A `.env` file in the repo root (copy from [`.env.example`](../../.env.example))

## Installation

From `apps/api/`:

```bash
uv sync
```

This creates the virtual environment and installs the exact dependencies specified in `uv.lock`.

## Starting the Development Server

First, make sure PostgreSQL is running ([see the root `README.md` in the repo](../../README.md)).

```bash
uv run fastapi dev app/main.py
```

The API is available at `http://localhost:8000`. Interactive documentation is available at `http://localhost:8000/docs`.

Health check endpoint (confirms an actual connection to the database):

```bash
curl http://localhost:8000/health
```

## Migrations (Alembic)

Create a new migration based on changes to the models:

```bash
uv run alembic revision --autogenerate -m "description of the change"
```

Apply pending migrations:

```bash
uv run alembic upgrade head
```

Revert the last migration:

```bash
uv run alembic downgrade -1
```

Connection credentials are read from `Settings` (`app/core/config.py`), the same source used by the application at runtime.

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

Made by [armandx06](https://github.com/armandx06) at July 28, 2026
