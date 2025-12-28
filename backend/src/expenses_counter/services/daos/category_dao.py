"""Category Data Access Object (DAO) module.

This module provides the CategoryDAO class for managing category-related database operations.
It extends the BaseDAO with category-specific functionality, including support for hierarchical
category relationships with parent categories loaded recursively.

Classes:
    CategoryDAO: Data access object for Category model operations with hierarchical support.
"""

__all__ = ("CategoryDAO",)

from typing import Literal

from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only, selectinload
from sqlalchemy.sql import ColumnElement

from expenses_counter.services.daos.base import BaseDAO, error_handler
from expenses_counter.services.database.models.category import Category


class CategoryDAO(BaseDAO[Category]):
    """Data Access Object for Category model operations.

    This DAO extends BaseDAO to provide category-specific database operations,
    with special handling for hierarchical category relationships. It supports
    loading parent categories recursively to build complete category hierarchies.

    Attributes:
        database_model: The Category SQLAlchemy model class.

    """

    database_model = Category

    async def _get_by_id_raw(self, session: AsyncSession, pk: int) -> Category:
        """Retrieve a single category by ID with all parent levels loaded recursively.

        This method overrides the base implementation to eagerly load the entire
        parent category hierarchy with unlimited recursion depth. This ensures
        that the complete category path from root to the requested category
        is available without additional queries.

        Args:
            session: The active database session.
            pk: The primary key of the category to retrieve.

        Returns:
            The Category model instance with all parent relationships loaded,
            or None if not found.

        """
        # Load all parent levels recursively (unlimited depth)
        stmt = select(Category).options(selectinload(Category.parent, recursion_depth=-1)).where(Category.id == pk)
        result = await session.execute(stmt)
        return result.scalar()

    async def _get_all_raw(
        self,
        session: AsyncSession,
        limit: int,
        offset: int,
        sort_by: str,
        sort_order: Literal["asc", "desc"],
        filters: list[ColumnElement[bool]] | None,
    ) -> list[Category]:
        """Retrieve multiple categories with pagination, sorting, and filtering.

        This method overrides the base implementation to optimize query performance
        by loading only the id and name fields. Parent relationships are not loaded
        in bulk queries for performance reasons.

        Args:
            session: The active database session.
            limit: Maximum number of records to return.
            offset: Number of records to skip for pagination.
            sort_by: The column name to sort by.
            sort_order: Sort direction, either "asc" or "desc".
            filters: Optional list of SQLAlchemy filter expressions.

        Returns:
            A list of Category model instances with limited fields loaded.

        """
        order_func = asc if sort_order == "asc" else desc
        stmt = (
            select(Category)
            .options(load_only(Category.id, Category.name))
            .limit(limit)
            .offset(offset)
            .order_by(order_func(getattr(Category, sort_by)))
        )
        if filters:
            stmt = stmt.where(*filters)

        result = await session.execute(stmt)
        return result.scalars().all()

    @error_handler
    async def get_all_by_parent(
        self,
        parent_id: int | None,
        limit: int = 100,
        offset: int = 0,
        sort_by: str = "id",
        sort_order: Literal["asc", "desc"] = "asc",
        filters: list[ColumnElement[bool]] | None = None,
    ) -> tuple[list[Category], int]:
        """Retrieve all categories that belong to a specific parent category.

        This method filters categories by their parent_id, allowing retrieval of
        direct children of a given parent category. Passing None as parent_id
        retrieves all top-level categories (those without a parent).

        Args:
            parent_id: The ID of the parent category to filter by, or None for top-level categories.
            limit: Maximum number of records to return. Defaults to 100.
            offset: Number of records to skip for pagination. Defaults to 0.
            sort_by: The column name to sort by. Defaults to "id".
            sort_order: Sort direction, either "asc" or "desc". Defaults to "asc".
            filters: Optional list of additional SQLAlchemy filter expressions.

        Returns:
            A tuple containing:
                - A list of Category model instances matching the criteria.
                - The total count of matching records (ignoring limit/offset).

        Raises:
            DBException: For general database errors.

        """
        additional_filters = [Category.parent_id == parent_id]
        filters = [*additional_filters, *(filters or [])]

        async with self.database_client.session_factory() as session:
            payload = await self._get_all_raw(session, limit, offset, sort_by, sort_order, filters)
            total = await self._get_all_count_raw(session, filters)
            return payload, total
