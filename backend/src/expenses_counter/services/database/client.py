"""Database client module."""

__all__ = ("DatabaseClient",)

from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

from expenses_counter.config import AppConfig
from expenses_counter.utils import Singleton


class DatabaseClient(metaclass=Singleton):
    """Async SQLAlchemy singleton database client.

    This class provides a singleton instance for managing async database connections
    using SQLAlchemy. It handles engine creation, session factory setup, and
    provides methods to obtain database sessions.

    Attributes:
        _engine: The SQLAlchemy async engine instance.
        _session_factory: Factory for creating async database sessions.

    """

    _engine = None
    _session_factory: async_sessionmaker[AsyncSession] | None = None

    def __init__(self, app_config: AppConfig | None = None) -> None:
        """Initialize the database client.

        Creates the async SQLAlchemy engine and session factory if not already
        initialized. Uses the provided app_config or retrieves the default
        configuration.

        Args:
            app_config: Optional application configuration. If not provided,
                the default AppConfig instance will be used.

        """
        if self._engine is None:
            config = app_config or AppConfig.get_or_create()
            self._engine = create_async_engine(
                config.services.database.url,
                echo=config.info.api_info.debug,
                future=True,
            )
            self._session_factory = async_sessionmaker[AsyncSession](
                self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Get the session factory.

        Returns:
            The session factory.

        """
        if self._session_factory is None:
            raise RuntimeError("Database client not initialized")
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

                from expenses_counter.services.database import DatabaseClient
                from expenses_counter.services.database.models import Category

                client = DatabaseClient()

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
        if self._session_factory is None:
            raise RuntimeError("Database client not initialized")
        async with self._session_factory() as session:
            yield session

    async def close(self) -> None:
        """Close the database engine and clean up resources.

        Disposes of the database engine and resets the session factory.
        This should be called when shutting down the application to properly
        clean up database connections.
        """
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None

    async def healthcheck(self) -> bool:
        """Check the health of the database client.

        Returns:
            True if the database client is healthy, False otherwise.

        """
        try:
            async with self._session_factory() as session:
                await session.execute(text("SELECT 1"))
        except Exception:
            return False
        return True
