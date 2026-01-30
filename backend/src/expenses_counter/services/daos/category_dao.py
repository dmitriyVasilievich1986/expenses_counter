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
from sqlalchemy.orm import load_only, selectinload
from sqlalchemy.sql import ColumnElement

from expenses_counter.services.daos.base import BaseDAO
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
    get_all_columns = (Category.id, Category.name)

    @BaseDAO.error_handler
    async def get_by_id(self, pk: int, pk_column_name: str | None = None) -> Category:
        """Retrieve a single category by ID with all parent levels loaded recursively.

        This method overrides the base implementation to eagerly load the entire
        parent category hierarchy with unlimited recursion depth. This ensures
        that the complete category path from root to the requested category
        is available without additional queries.

        Args:
            pk: The primary key of the category to retrieve.
            pk_column_name: The name of the primary key column to use.

        Returns:
            The Category model instance with all parent relationships loaded,
            or None if not found.

        """
        pk_column_name = pk_column_name or self.pk_column_name
        # Load all parent levels recursively (unlimited depth)
        stmt = (
            select(Category)
            .options(selectinload(Category.parent, recursion_depth=-1))
            .where(getattr(Category, pk_column_name) == pk)
        )
        if self.select_in_options_single:
            stmt = stmt.options(*map(selectinload, self.select_in_options_single))

        result = await self.session.execute(stmt)
        return result.scalar_one()

    @BaseDAO.error_handler
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

        """
        filters = [*(filters or []), Category.parent_id == parent_id]

        order_func = asc if sort_order == "asc" else desc
        stmt = select(self.database_model).order_by(order_func(getattr(self.database_model, sort_by))).where(*filters)

        if self.get_all_columns:
            stmt = stmt.options(load_only(*self.get_all_columns))

        if self.select_in_options_all:
            stmt = stmt.options(*map(selectinload, self.select_in_options_all))

        if limit:
            stmt = stmt.limit(limit)
        if offset:
            stmt = stmt.offset(offset)

        result = await self.session.execute(stmt)
        total = await self.get_total(filters)
        return result.scalars().all(), total
