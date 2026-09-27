import os

from alembic.config import Config
from sqlalchemy.orm import Session, SessionTransaction

from alembic import command
from app.models.base import Base

os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_TESTDB_HOST", "localhost")

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from app.core.config import settings
from app.db.session import get_db, get_test_db, test_engine
from app.main import app


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession]:
    engine = create_async_engine(settings.database_url)

    async with engine.connect() as connection:
        await connection.begin()
        session = AsyncSession(bind=connection, expire_on_commit=False)

        await connection.begin_nested()

        @event.listens_for(session.sync_session, "after_transaction_end")
        def restart_savepoint(
            _sync_session: Session, _transaction: SessionTransaction
        ) -> None:
            sync_connection = connection.sync_connection
            if (
                sync_connection is not None
                and not sync_connection.in_nested_transaction()
            ):
                sync_connection.begin_nested()

        yield session

        await session.close()
        await connection.rollback()

    await engine.dispose()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient]:
    async def override_get_db() -> AsyncGenerator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


def _run_test_migrations() -> None:
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.test_database_url)
    command.upgrade(alembic_cfg, "head")


@pytest.fixture(scope="session", autouse=True)
def apply_test_migrations() -> None:
    _run_test_migrations()


async def truncate_all_tables(engine: AsyncEngine) -> None:
    table_names = [table.name for table in Base.metadata.sorted_tables]
    if not table_names:
        return

    tables = ", ".join(table_names)
    async with engine.begin() as conn:
        await conn.execute(text(f"TRUNCATE TABLE {tables} RESTART IDENTITY CASCADE"))


@pytest.fixture
async def concurrent_client() -> AsyncGenerator[AsyncClient]:
    app.dependency_overrides[get_db] = get_test_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    await truncate_all_tables(test_engine)
