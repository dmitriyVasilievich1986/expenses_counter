"""Database client module."""

__all__ = ("AsyncDatabaseClient",)

from typing import AsyncGenerator

from loguru import logger
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine, AsyncSession, create_async_engine

from expenses_counter.config import AppConfig
from expenses_counter.utils import Singleton


class AsyncDatabaseClient(metaclass=Singleton):
    """Async SQLAlchemy singleton database client.

    This class provides a singleton instance for managing async database connections
    using SQLAlchemy. It handles engine creation, session factory setup, and
    provides methods to obtain database sessions.

    Attributes:
        _engine: The SQLAlchemy async engine instance.
        _session_factory: Factory for creating async database sessions.

    """

    _engine: AsyncEngine
    _session_factory: async_sessionmaker[AsyncSession]

    def __init__(self, app_config: AppConfig | None = None) -> None:
        """Initialize the database client.

        Creates the async SQLAlchemy engine and session factory if not already
        initialized. Uses the provided app_config or retrieves the default
        configuration.

        Args:
            app_config: Optional application configuration. If not provided,
                the default AppConfig instance will be used.

        """
        if app_config is None:
            raise RuntimeError("App config is required")
        logger.info(f"Initializing database client with URL: {app_config.services.database.url}")

        self._engine = create_async_engine(
            app_config.services.database.url,
            echo=app_config.info.api_info.debug,
            future=True,
        )
        self._session_factory = async_sessionmaker[AsyncSession](
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        logger.info("Database client initialized successfully.")

    @property
    def engine(self) -> AsyncEngine:
        """Get the database engine.

        Returns:
            The database engine.

        """
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Get the session factory.

        Returns:
            The session factory.

        """
        return self._session_factory

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session.

        Creates and yields an async database session from the session factory.
        The session is automatically closed when exiting the context.

        Yields:
            An async SQLAlchemy session that can be used for database operations.

        Raises:
            RuntimeError: If the database client has not been initialized.

        Example:
            Basic usage for querying:

            .. code-block:: python

                from expenses_counter.services.database import AsyncDatabaseClient
                from expenses_counter.services.database.models import Category

                client = AsyncDatabaseClient()

                # Query example
                async for session in client.get_session():
                    result = await session.execute(
                        select(Category).where(Category.name == "Groceries")
                    )
                    category = result.scalar_one_or_none()

        Example:
                Creating a new record:

            .. code-block:: python

                async for session in client.get_session():
                    new_category = Category(name="Electronics", description="Tech items")
                    session.add(new_category)
                    await session.commit()

        Example:
                Updating a record:

            .. code-block:: python

                async for session in client.get_session():
                    result = await session.execute(
                        select(Category).where(Category.id == 1)
                    )
                    category = result.scalar_one()
                    category.name = "Updated Name"
                    await session.commit()

        """
        async with self._session_factory() as session:
            yield session

    async def close(self) -> None:
        """Close the database engine and clean up resources.

        Disposes of the database engine and resets the session factory.
        This should be called when shutting down the application to properly
        clean up database connections.
        """
        await self._engine.dispose()
        logger.info("Database client closed successfully.")

    async def healthcheck(self) -> bool:
        """Check the health of the database client.

        Executes a simple SELECT query to verify database connectivity and
        operational status.

        Returns:
            True if the database client is healthy and can execute queries,
            False if any SQLAlchemy error occurs during the health check.

        """
        try:
            async with self._session_factory() as session:
                await session.execute(text("SELECT 1"))
        except SQLAlchemyError as e:
            logger.error(f"Database health check failed: {e}")
            return False

        return True
