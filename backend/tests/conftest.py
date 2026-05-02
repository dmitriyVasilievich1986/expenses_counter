"""Pytest configuration and fixtures for backend testing.

This module provides session-level fixtures for database testing, including
test database creation, migration execution, and database client setup.
"""

import asyncio
from pathlib import Path
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig

from expenses_counter.config import AppConfig
from expenses_counter.config.base.storage import SettingsStorage
from expenses_counter.services.database import AsyncDatabaseClient
from expenses_counter.utils.singleton import Singleton


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session.

    This fixture ensures that async fixtures can run at the session scope.
    By default, pytest-asyncio creates a new event loop for each test function,
    but we need a session-scoped event loop for session-scoped async fixtures.

    Yields:
        asyncio.AbstractEventLoop: The event loop for the test session.

    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_db_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Create a temporary path for the test database.

    Args:
        tmp_path_factory: Pytest fixture for creating temporary directories.

    Returns:
        Path: The path to the test database file.

    """
    tmp_dir = tmp_path_factory.mktemp("test_db")
    return tmp_dir / "test_db.sqlite"


@pytest.fixture(scope="session")
def test_config(test_db_path: Path) -> AppConfig:
    """Create a test configuration with SQLite database.

    This fixture creates an AppConfig instance configured to use a SQLite
    test database. It bypasses the YAML configuration loading by directly
    constructing the config object.

    Args:
        test_db_path: Path to the test database file.

    Returns:
        AppConfig: Configuration instance for testing.

    """
    from expenses_counter.config.models.info import Info
    from expenses_counter.config.models.info.api import APIInfo
    from expenses_counter.config.models.info.cors import CORSInfo
    from expenses_counter.config.models.services import Services
    from expenses_counter.config.models.services.database import Database

    # Create config without loading from YAML
    config = AppConfig(
        info=Info(
            name="Expenses Counter Test",
            description="Test configuration",
            api_info=APIInfo(
                app_port=8000,
                debug=True,
                log_level="DEBUG",
            ),
            cors_info=CORSInfo(
                origins="*",
                allow_credentials=True,
                allow_methods=["GET", "POST", "PUT", "DELETE"],
                allow_headers=["*"],
            ),
        ),
        services=Services(
            database=Database(
                provider="sqlite+aiosqlite",
                host=str(test_db_path),
            ),
        ),
    )

    # Store in SettingsStorage to make it available via get_or_create()
    storage = SettingsStorage()
    storage.settings = config

    return config


@pytest_asyncio.fixture(scope="session")
async def test_database_with_migrations(
    test_config: AppConfig,  # noqa: ARG001
    test_db_path: Path,
) -> AsyncGenerator[Path, None]:
    """Create test database and apply schema via Alembic migrations.

    This fixture:
    1. Creates a fresh test database using SQLite
    2. Runs Alembic ``upgrade head`` to apply all migrations
    3. Yields the database path for tests to use
    4. Cleans up after all tests complete

    Alembic is run in a worker thread so its internal ``asyncio.run()`` call
    does not conflict with the already-running pytest-asyncio event loop.
    The migration env.py picks up the test database URL automatically via
    ``AppConfig.get_or_create()``, which reads from the singleton
    ``SettingsStorage`` populated by the ``test_config`` fixture.

    Args:
        test_config: Test configuration with database settings (stored in
            SettingsStorage so Alembic env.py can find it).
        test_db_path: Path to the test database file.

    Yields:
        Path: Path to the test database with all migrations applied.

    """
    _alembic_ini = Path(__file__).parent.parent / "src" / "expenses_counter" / "services" / "alembic" / "alembic.ini"

    def _run_migrations() -> None:
        cfg = AlembicConfig(str(_alembic_ini))
        alembic_command.upgrade(cfg, "head")

    try:
        await asyncio.to_thread(_run_migrations)

        yield test_db_path

    finally:
        if test_db_path.exists():
            test_db_path.unlink()


@pytest_asyncio.fixture(scope="session")
async def async_db_client(
    test_config: AppConfig,
    test_database_with_migrations: Path,  # noqa: ARG001
) -> AsyncGenerator[AsyncDatabaseClient, None]:
    """Create and configure AsyncDatabaseClient for testing.

    This fixture provides a session-scoped AsyncDatabaseClient instance
    connected to the test database. The client uses the Singleton pattern,
    which is properly cleared after all tests complete. The test database
    file is automatically dropped after the test session ends.

    Args:
        test_config: Test configuration with database settings.
        test_database_with_migrations: Path to test database.

    Yields:
        AsyncDatabaseClient: Database client instance for testing.

    """
    # Clear any existing singleton instances
    Singleton._instances.clear()  # noqa: SLF001

    # Create the database client
    client = AsyncDatabaseClient(app_config=test_config)

    # Verify connection works
    assert await client.healthcheck(), "Database health check failed"

    yield client

    # Cleanup: close the client and clear singleton
    await client.close()
    Singleton._instances.clear()  # noqa: SLF001

    # Clear settings storage
    storage = SettingsStorage()
    storage.settings = None


@pytest_asyncio.fixture
async def db_session(async_db_client: AsyncDatabaseClient):
    """Provide a database session for individual tests.

    This fixture provides a transactional database session that is rolled back
    after each test, ensuring test isolation. Each test gets a clean database
    state without needing to recreate the entire database.

    The fixture uses a nested transaction (savepoint) to ensure that even
    explicit commits within the test are rolled back after the test completes.

    Args:
        async_db_client: The session-scoped database client.

    Yields:
        AsyncSession: A database session for the test.

    """
    # Get a connection from the engine
    async with async_db_client.engine.connect() as connection:
        # Start a transaction
        async with connection.begin() as transaction:
            # Create a session bound to this connection
            from sqlalchemy.ext.asyncio import AsyncSession

            session = AsyncSession(bind=connection, expire_on_commit=False)

            try:
                yield session
            finally:
                await session.close()
                # Rollback the transaction
                await transaction.rollback()
