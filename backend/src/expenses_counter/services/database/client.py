"""Database client module for managing SQLAlchemy connections and sessions."""

__all__ = ("DatabaseClient",)

from typing import Generator

from loguru import logger
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker

from expenses_counter.config import AppConfig
from expenses_counter.utils import Singleton


class DatabaseClient(metaclass=Singleton):
    """Singleton database client for managing SQLAlchemy connections.

    This client provides a centralized interface for database operations,
    including connection management, session creation, and resource cleanup.
    Uses the Singleton pattern to ensure only one database connection pool
    exists throughout the application lifecycle.

    Attributes:
        _engine: SQLAlchemy engine instance for database connections
        _session_factory: Session factory for creating database sessions

    """

    _engine: Engine
    _session_factory: sessionmaker[Session]

    def __init__(self, app_config: AppConfig | None = None) -> None:
        """Initialize DatabaseClient with application configuration.

        Creates a SQLAlchemy engine and session factory based on the provided
        configuration. The engine connection pool and debug mode are configured
        from the app config.

        Args:
            app_config: Application configuration containing database settings

        Raises:
            RuntimeError: If app_config is None

        Note:
            Due to Singleton pattern, subsequent calls with different configs
            will not reinitialize the client.

        """
        if app_config is None:
            raise RuntimeError("App config is required")
        logger.info(f"Initializing database client with URL: {app_config.services.database.url}")

        self._engine = create_engine(
            app_config.services.database.url,
            echo=app_config.info.api_info.debug,
            future=True,
        )
        self._session_factory = sessionmaker[Session](
            self._engine,
            class_=Session,
            expire_on_commit=False,
        )
        logger.info("Database client initialized successfully.")

    @property
    def engine(self) -> Engine:
        """Get the SQLAlchemy engine instance.

        Returns:
            The database engine used for low-level database operations

        """
        return self._engine

    @property
    def session_factory(self) -> Session:
        """Get the session factory for creating database sessions.

        Returns:
            Session factory configured with the database engine

        """
        return self._session_factory

    def get_session(self) -> Generator[Session, None, None]:
        """Create and yield a database session with automatic cleanup.

        This context manager provides a database session that is automatically
        closed when the context exits, ensuring proper resource management.

        Yields:
            SQLAlchemy Session instance for database operations

        Example:
            >>> db_client = DatabaseClient(app_config)
            >>> for session in db_client.get_session():
            ...     user = session.query(User).first()
            ...     # Session is automatically closed after the loop

        """
        with self._session_factory() as session:
            yield session

    def close(self) -> None:
        """Close the database connection pool and release resources.

        Disposes of the SQLAlchemy engine, closing all connections in the pool.
        This should be called during application shutdown to ensure clean
        resource cleanup.

        Note:
            After calling this method, the client should not be used for
            database operations.

        """
        self._engine.dispose()
        logger.info("Database client closed successfully.")
