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

from abc import ABC
from typing import Any, Generic, Literal, Type, TypeVar

from loguru import logger
from pydantic import BaseModel
from sqlalchemy import asc, desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql import ColumnElement

from expenses_counter.services.database import DatabaseClient
from expenses_counter.services.database.models.base import Base

from .error_handler import error_handler

B = TypeVar("B", bound=Type[Base])
R = TypeVar("R", bound=Type[BaseModel])


class BaseDAO(ABC, Generic[B]):
    """Abstract base class for Data Access Objects.

    This class provides common CRUD (Create, Read, Update, Delete) operations
    for database models. It handles database sessions, error handling, and
    provides both raw and decorated methods for database operations.

    Attributes:
        database_model: The SQLAlchemy model class this DAO operates on.
        database_client: The database client instance for managing connections.

    Type Parameters:
        B: The SQLAlchemy Base model type this DAO operates on.

    """

    database_model: type[B]
    get_all_columns: tuple[InstrumentedAttribute, ...]

    def __init__(self, database_client: DatabaseClient, **_: Any) -> None:
        """Initialize the BaseDAO with a database client.

        Args:
            database_client: The database client used for database operations.
            **_: Additional keyword arguments (reserved for subclass use).

        """
        self.database_client = database_client

    async def _get_by_id_raw(self, session: AsyncSession, pk: int) -> B:
        """Retrieve a single database record by its primary key.

        This is a raw method that works within an existing session context.

        Args:
            session: The active database session.
            pk: The primary key of the record to retrieve.

        Returns:
            The database model instance, or None if not found.

        """
        stmt = select(self.database_model).where(self.database_model.id == pk)
        result = await session.execute(stmt)
        return result.scalar()

    @error_handler
    async def get_by_id(self, pk: int) -> B:
        """Retrieve a single database record by its primary key.

        This method manages its own session and includes error handling.

        Args:
            pk: The primary key of the record to retrieve.

        Returns:
            The database model instance.

        Raises:
            NotFoundException: If the record is not found.
            DBException: For general database errors.

        """
        async with self.database_client.session_factory() as session:
            return await self._get_by_id_raw(session, pk)

    async def _get_all_raw(
        self,
        session: AsyncSession,
        limit: int,
        offset: int,
        sort_by: str,
        sort_order: Literal["asc", "desc"],
        filters: list[ColumnElement[bool]] | None,
    ) -> list[B]:
        """Retrieve multiple database records with pagination, sorting, and filtering.

        This is a raw method that works within an existing session context.

        Args:
            session: The active database session.
            limit: Maximum number of records to return.
            offset: Number of records to skip for pagination.
            sort_by: The column name to sort by.
            sort_order: Sort direction, either "asc" or "desc".
            filters: Optional list of SQLAlchemy filter expressions.

        Returns:
            A list of database model instances.

        """
        order_func = asc if sort_order == "asc" else desc
        stmt = (
            select(self.database_model)
            .options(load_only(*self.get_all_columns))
            .limit(limit)
            .offset(offset)
            .order_by(order_func(getattr(self.database_model, sort_by)))
        )

        if filters:
            stmt = stmt.where(*filters)

        result = await session.execute(stmt)
        return result.scalars().all()

    async def _get_all_count_raw(self, session: AsyncSession, filters: list[ColumnElement[bool]] | None) -> int:
        """Count the total number of records matching the given filters.

        This is a raw method that works within an existing session context.

        Args:
            session: The active database session.
            filters: Optional list of SQLAlchemy filter expressions.

        Returns:
            The total count of matching records.

        """
        stmt = select(func.count()).select_from(self.database_model)
        if filters:
            stmt = stmt.where(*filters)

        result = await session.execute(stmt)
        return result.scalar_one()

    @error_handler
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        sort_by: str = "id",
        sort_order: Literal["asc", "desc"] = "asc",
        filters: list[ColumnElement[bool]] | None = None,
    ) -> tuple[list[B], int]:
        """Retrieve multiple database records with pagination, sorting, and filtering.

        This method manages its own session and includes error handling.

        Args:
            limit: Maximum number of records to return. Defaults to 100.
            offset: Number of records to skip for pagination. Defaults to 0.
            sort_by: The column name to sort by. Defaults to "id".
            sort_order: Sort direction, either "asc" or "desc". Defaults to "asc".
            filters: Optional list of SQLAlchemy filter expressions. Defaults to None.

        Returns:
            A tuple containing:
                - A list of database model instances
                - The total count of matching records (before pagination)

        Raises:
            DBException: For general database errors.

        """
        async with self.database_client.session_factory() as session:
            payload = await self._get_all_raw(session, limit, offset, sort_by, sort_order, filters)
            total = await self._get_all_count_raw(session, filters)
            return payload, total

    async def _create_raw(self, session: AsyncSession, **kwargs) -> B:
        """Create a new database record.

        This is a raw method that works within an existing session context.

        Args:
            session: The active database session.
            **kwargs: Field values for the new record.

        Returns:
            The newly created database model instance.

        """
        obj = self.database_model(**kwargs)
        session.add(obj)
        await session.commit()
        return await self._get_by_id_raw(session, obj.id)

    @error_handler
    async def create(self, **kwargs) -> B:
        """Create a new database record.

        This method manages its own session and includes error handling.

        Args:
            **kwargs: Field values for the new record.

        Returns:
            The newly created database model instance.

        Raises:
            RelationshipNotFoundException: When a foreign key constraint is violated.
            DBException: For general database errors.

        """
        async with self.database_client.session_factory() as session:
            payload = await self._create_raw(session, **kwargs)
            logger.debug(f"Instance created: {payload.id}")
            return payload

    async def _update_raw(self, session: AsyncSession, pk: int, **kwargs: Any) -> B:
        """Update an existing database record.

        This is a raw method that works within an existing session context.

        Args:
            session: The active database session.
            pk: The primary key of the record to update.
            **kwargs: Field values to update.

        Returns:
            The updated database model instance.

        """
        await session.execute(update(self.database_model).where(self.database_model.id == pk).values(**kwargs))
        await session.commit()

        return await self._get_by_id_raw(session, pk)

    @error_handler
    async def update(self, pk: int, **kwargs: Any) -> B:
        """Update an existing database record.

        This method manages its own session and includes error handling.

        Args:
            pk: The primary key of the record to update.
            **kwargs: Field values to update.

        Returns:
            The updated database model instance.

        Raises:
            NotFoundException: If the record is not found.
            RelationshipNotFoundException: When a foreign key constraint is violated.
            DBException: For general database errors.

        """
        async with self.database_client.session_factory() as session:
            payload = await self._update_raw(session, pk, **kwargs)
            logger.debug(f"Instance updated: {payload.id}")
            return payload

    async def _delete_raw(self, session: AsyncSession, pk: int) -> bool:
        """Delete a database record by its primary key.

        This is a raw method that works within an existing session context.

        Args:
            session: The active database session.
            pk: The primary key of the record to delete.

        Returns:
            True if the record was deleted, False if not found.

        """
        if (instance := await self._get_by_id_raw(session, pk)) is None:
            logger.debug(f"Instance not found: {pk}")
            return False

        await session.delete(instance)
        await session.commit()
        logger.debug(f"Instance deleted: {pk}")
        return True

    @error_handler
    async def delete(self, pk: int) -> bool:
        """Delete a database record by its primary key.

        This method manages its own session and includes error handling.

        Args:
            pk: The primary key of the record to delete.

        Returns:
            True if the record was deleted, False if not found.

        Raises:
            RelationshipNotFoundException: When foreign key constraints prevent deletion.
            DBException: For general database errors.

        """
        async with self.database_client.session_factory() as session:
            payload = await self._delete_raw(session, pk)
            logger.debug(f"Instance deleted: {pk}")
            return payload
