"""Category Data Access Object (DAO) module.

This module provides the CategoryDAO class for managing category-related database operations.
It extends the BaseDAO with category-specific functionality, including support for hierarchical
category relationships with parent categories loaded recursively.

Classes:
    CategoryDAO: Data access object for Category model operations with hierarchical support.
"""

__all__ = ("CategoryDAO",)


from sqlalchemy import select
from sqlalchemy.orm import selectinload

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
