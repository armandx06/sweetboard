# ADR 0002: Asynchronous Database Access with SQLAlchemy 2.0 and asyncpg

- **Status:** Accepted
- **Date:** 2026-07-28
- **Decider:** Jorge Armando Ceras Cárdenas - [armandx06](https://github.com/armandx06)

## Context and Problem Statement

The application runs on an asynchronous, non-blocking I/O web framework. We need to define the database access layer strategy for PostgreSQL.

Traditional synchronous ORM access forces the async event loop to block during database I/O or offload calls to thread pools, introducing unnecessary overhead and limiting concurrency. Furthermore, using different database drivers or connection paradigms between runtime execution and schema migrations (Alembic) often introduces configuration drift, duplicate environment variables, and subtle driver-level inconsistencies.

## Decision Drivers

- **Performance & Throughput:** Maximizing concurrent request processing without thread-blocking I/O bottlenecks.
- **Single Source of Truth:** Unifying database configuration (`DATABASE_URL`) across runtime application logic and Alembic schema migrations.
- **Maintainability:** Avoiding hybrid sync/async codebase patterns and minimizing driver fragmentation.
- **Type Safety & Standards:** Utilizing modern SQLAlchemy 2.0 asynchronous patterns (`AsyncSession`, `select()` style statements).

## Considered Options

1. Synchronous SQLAlchemy with `psycopg2` / `psycopg3` (Sync)
2. **Hybrid:** Asynchronous SQLAlchemy for runtime API + Synchronous Alembic for migrations
3. **Fully Asynchronous:** SQLAlchemy 2.0 AsyncEngine + `asyncpg` driver for both runtime and Alembic migrations

## Decision Outcome

Chosen option: **Option 3 (Fully Asynchronous SQLAlchemy 2.0 with `asyncpg`)**.

We will adopt an end-to-end asynchronous architecture using SQLAlchemy 2.0 (`AsyncEngine`, `async_sessionmaker`, `AsyncSession`) alongside the `asyncpg` driver for all database operations, including schema migrations managed by Alembic.

### Implementation Details

#### 1. Centralized Configuration

The database connection string will be managed exclusively via the application's `Settings` module (e.g., `pydantic-settings`).

- Protocol: `postgresql+asyncpg://user:pass@host:5432/dbname`
- Both runtime dependency injection and Alembic's `env.py` will import this setting directly.

#### 2. Session Lifecycle & Engine

- A single, global `AsyncEngine` instance will manage the connection pool.
- Sessions will be instantiated via `async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)`.
- HTTP request handlers will receive scoped `AsyncSession` instances via context managers / framework dependency injection, ensuring explicit cleanup and transaction rollback on unhandled exceptions.

#### 3. Asynchronous Alembic Migrations

Alembic's `env.py` will be configured to execute migrations asynchronously using `asyncio.run()` and `connection.run_sync()`:

```python
import asyncio
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from app.core.config import settings

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def run_migrations_online():
    asyncio.run(run_async_migrations())
```

## Consequences

### Positive

- **High Concurrency:** Full non-blocking I/O pipeline from API routing down to database queries.
- **Environment Parity:** Identical driver behavior, dialect handling, and connection strings across development, production, and migration tasks.
- **Resource Efficiency:** Reduced memory footprint compared to multi-threaded synchronous workers.

### Negative / Trade-offs

- **Eager Loading Constraints:** Implicit lazy loading of relationships is disabled in `AsyncSession`. All relationships must be explicitly loaded using `selectinload()`, `joinedload()`, or configured for async execution to prevent `MissingGreenlet` errors.
- **Third-Party Compatibility:** Libraries relying on synchronous DBAPI interfaces will require async adapters or explicit thread wrapping.
- **Debugging Complexity:** Asynchronous stack traces and transaction scopes require higher developer discipline regarding session boundaries and error handling.

---

Made by [armandx06](https://github.com/armandx06) at July 28, 2026
