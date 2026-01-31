"""Base Data Access Object (DAO) module.

This module provides the abstract base class for all DAO implementations in the application.
The BaseDAO class offers common CRUD operations and error handling for database interactions,
using SQLAlchemy async sessions and providing a consistent interface for data persistence.

Classes:
    BaseDAO: Abstract base class for data access objects with generic CRUD operations.

Type Variables:
    B: Type variable bound to SQLAlchemy Base models.
    R: Type variable bound to Pydantic BaseModel for responses.
"""

__all__ = ("BaseDAO",)

import socket
from abc import ABC
from functools import wraps
from types import TracebackType
from typing import Any, Callable, Literal, Self, TypeVar

from loguru import logger
from sqlalchemy import asc, desc, func, select, update
from sqlalchemy.exc import DatabaseError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only, selectinload
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql import ColumnElement

from expenses_counter.services.database import AsyncDatabaseClient
from expenses_counter.services.database.models.base import Base

R = TypeVar("R")


class BaseDAO[DatabaseModel: Base](ABC):
    """Abstract base class for Data Access Objects.

    This class provides a generic interface for CRUD operations on database models,
    with support for async context management, error handling, and flexible querying.

    Attributes:
        database_model: The SQLAlchemy model class this DAO operates on.
        get_all_columns: Optional tuple of columns to load when fetching all records.
        select_in_options_single: Optional tuple of relationships to eager load for single record queries.
        select_in_options_all: Optional tuple of relationships to eager load for multiple record queries.

    """

    pk_column_name: str = "id"
    database_model: type[DatabaseModel]
    get_all_columns: tuple[InstrumentedAttribute, ...] | None = None
    select_in_options_single: tuple[InstrumentedAttribute, ...] | None = None
    select_in_options_all: tuple[InstrumentedAttribute, ...] | None = None

    def __init__(self, database_client: AsyncDatabaseClient, session: AsyncSession | None = None, **_: Any) -> None:
        """Initialize the DAO with a database client and optional session.

        Args:
            database_client: The async database client for creating sessions.
            session: Optional pre-existing async session to use.
            **_: Additional keyword arguments (ignored).

        """
        self.database_client = database_client
        self._session = session

    @staticmethod
    def error_handler(func: Callable[..., R]) -> Callable[..., R]:
        """Decorator for handling and logging errors in DAO methods.

        Args:
            func: The async function to wrap with error handling.

        Returns:
            The wrapped function with error handling and logging.

        """

        @wraps(func)
        async def wrapper(self: "BaseDAO", *args: Any, **kwargs: Any) -> R:
            try:
                return await func(self, *args, **kwargs)
            except (ConnectionRefusedError, socket.gaierror) as e:
                logger.exception("Database connection refused")
                raise DatabaseError("Database connection refused", None, e) from e
            except DatabaseError:
                logger.exception("Database error")

        return wrapper

    @property
    def session(self) -> AsyncSession:
        """Get the current async database session.

        Returns:
            The active AsyncSession instance.

        Raises:
            ValueError: If no session has been set.

        """
        if self._session is None:
            raise ValueError("Session is not set")

        return self._session

    async def __aenter__(self) -> Self:
        """Enter the async context manager, creating a new database session.

        Returns:
            The DAO instance with an active session.

        """
        self._session = self.database_client.session_factory()
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None
    ) -> None:
        """Exit the async context manager, closing the database session.

        Args:
            exc_type: The type of exception raised, if any.
            exc_value: The exception instance raised, if any.
            traceback: The traceback object, if any.

        """
        await self.session.aclose()

    @error_handler
    async def get_by_id(self, pk: int, pk_column_name: str | None = None) -> DatabaseModel:
        """Retrieve a single record by its primary key.

        Args:
            pk: The primary key (ID) of the record to retrieve.
            pk_column_name: The name of the primary key column to use.

        Returns:
            The database model instance, or None if not found.

        """
        pk_column_name = pk_column_name or self.pk_column_name
        stmt = select(self.database_model).where(getattr(self.database_model, pk_column_name) == pk)

        if self.select_in_options_single:
            stmt = stmt.options(*map(selectinload, self.select_in_options_single))

        result = await self.session.execute(stmt)
        return result.scalar_one()

    @error_handler
    async def get_total(self, filters: list[ColumnElement[bool]] | None) -> int:
        """Get the total count of records matching the given filters.

        Args:
            filters: Optional list of SQLAlchemy filter expressions to apply.

        Returns:
            The total count of matching records.

        """
        stmt = select(func.count()).select_from(self.database_model)
        if filters:
            stmt = stmt.where(*filters)

        result = await self.session.execute(stmt)
        return result.scalar_one()

    @error_handler
    async def get_all(
        self,
        limit: int | None = 100,
        offset: int | None = 0,
        sort_by: str = "id",
        sort_order: Literal["asc", "desc"] = "asc",
        filters: list[ColumnElement[bool]] | None = None,
    ) -> tuple[list[DatabaseModel], int]:
        """Retrieve all records with pagination, sorting, and filtering.

        Args:
            limit: Maximum number of records to return (default: 100).
            offset: Number of records to skip (default: 0).
            sort_by: Column name to sort by (default: "id").
            sort_order: Sort direction, either "asc" or "desc" (default: "asc").
            filters: Optional list of SQLAlchemy filter expressions to apply.

        Returns:
            A tuple containing:
                - List of database model instances matching the criteria.
                - Total count of records matching the filters (ignoring pagination).

        """
        order_func = asc if sort_order == "asc" else desc
        stmt = select(self.database_model).order_by(order_func(getattr(self.database_model, sort_by)))

        if self.get_all_columns:
            stmt = stmt.options(load_only(*self.get_all_columns))

        if self.select_in_options_all:
            stmt = stmt.options(*map(selectinload, self.select_in_options_all))

        if limit:
            stmt = stmt.limit(limit)
        if offset:
            stmt = stmt.offset(offset)
        if filters:
            stmt = stmt.where(*filters)

        total = await self.get_total(filters)
        result = await self.session.execute(stmt)
        return result.scalars().all(), total

    @error_handler
    async def create(self, **kwargs) -> DatabaseModel:
        """Create a new record in the database.

        Args:
            **kwargs: Field values for the new record.

        Returns:
            The created database model instance with all relationships loaded.

        """
        obj = self.database_model(**kwargs)
        self.session.add(obj)
        await self.session.commit()
        return await self.get_by_id(obj.id)

    @error_handler
    async def update(self, pk: int, pk_column_name: str | None = None, **kwargs: Any) -> DatabaseModel:
        """Update an existing record by its primary key.

        Args:
            pk: The primary key (ID) of the record to update.
            pk_column_name: The name of the primary key column to use.
            **kwargs: Field values to update.

        Returns:
            The updated database model instance with all relationships loaded.

        """
        pk_column_name = pk_column_name or self.pk_column_name
        await self.session.execute(
            update(self.database_model).where(getattr(self.database_model, pk_column_name) == pk).values(**kwargs)
        )
        await self.session.commit()

        return await self.get_by_id(pk)

    @error_handler
    async def delete(self, pk: int, pk_column_name: str | None = None) -> bool:
        """Delete a record by its primary key.

        Args:
            pk: The primary key (ID) of the record to delete.
            pk_column_name: The name of the primary key column to use.

        Returns:
            True if the deletion was successful.

        """
        pk_column_name = pk_column_name or self.pk_column_name
        instance = await self.get_by_id(pk, pk_column_name)
        await self.session.delete(instance)
        await self.session.commit()
        return True
