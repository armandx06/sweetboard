from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings

# TODO: Remove the “echo” after debugging
engine = create_async_engine(settings.database_url, echo=True)
test_engine = create_async_engine(settings.test_database_url, echo=True)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
AsyncSessionLocalTest = async_sessionmaker(test_engine, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def get_test_db():
    async with AsyncSessionLocalTest() as session:
        yield session
