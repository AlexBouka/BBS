import asyncio
import pytest
import httpx
from httpx import ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from main import app
from core.database import Base
from core.config import settings
from core.db_handler import db_handler
from .test_utils import create_test_admin_user

TEST_DB_URL = (
    f"postgresql+asyncpg://{settings.postgres_test_user}:{settings.postgres_test_password}"
    f"@{settings.postgres_test_host}:{settings.postgres_test_port}/{settings.postgres_test_db}"
    )


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """
    A pytest fixture that sets up a test database.

    The fixture creates a database connection to the test database,
    creates all tables in the database, and creates a test admin user.
    It then yields control to the test, allowing the test to use
    the database connection.

    After the test is finished, the fixture drops all tables in
    the database and closes the database connection.

    :yields: The database connection to use.
    :rtype: AsyncSession
    """

    async def _setup():
        engine = create_async_engine(url=TEST_DB_URL, echo=False, pool_pre_ping=True)

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session() as session:
            try:
                await create_test_admin_user(session)
            except Exception as e:
                print(f"Warning: Failed to create admin user in test DB: {e}")

        # Store engine globally for cleanup
        global _test_engine
        _test_engine = engine

    asyncio.run(_setup())

    yield

    async def _cleanup():
        try:
            if '_test_engine' in globals():
                async with _test_engine.begin() as conn:
                    await conn.run_sync(Base.metadata.drop_all)
                await _test_engine.dispose()
        except Exception as e:
            print(f"Warning: Failed to clean up test DB: {e}")

    asyncio.run(_cleanup())


@pytest.fixture
def client():
    """
    A pytest fixture that provides an HTTPX AsyncClient for testing purposes.
    Overrides the DB dependency to use the test database.

    :returns: An HTTPX AsyncClient object
    :rtype: httpx.AsyncClient
    """
    test_engine = create_async_engine(
        url=TEST_DB_URL, echo=False, pool_pre_ping=True)

    async def get_test_session():
        async with AsyncSession(test_engine) as session:
            yield session

    app.dependency_overrides[db_handler.session_dependency] = get_test_session

    client = httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver")
    yield client
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
async def db_session():
    """
    A pytest fixture that provides an asynchronous
    database session for testing purposes.

    The fixture creates a database session at the start of the test and
    closes it at the end of the test, ensuring that any data
    created during the test is properly cleaned up.

    :yields: An asynchronous database session object
    :rtype: sqlalchemy.ext.asyncio.AsyncSession
    """
    engine = create_async_engine(url=TEST_DB_URL, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session
