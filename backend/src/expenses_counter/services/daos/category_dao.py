"""Async DAO for category rows with hierarchical parent loading."""

__all__ = ("CategoryDAO",)


from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import ColumnElement

from expenses_counter.services.daos.base import BaseDAO
from expenses_counter.services.database.models.category import Category


class CategoryDAO(BaseDAO[Category]):
    """Data access for ``Category`` with unlimited-depth ``parent`` eager load."""

    database_model = Category
    get_all_columns = (Category.id, Category.name)

    async def _get_by_pk_raw(
        self,
        session: AsyncSession,
        pk: int | str,
        pk_column_name: str,
        filters: list[ColumnElement[bool]] | list[dict[str, Any]] | None = None,
    ) -> Category:
        """Load one category by primary key with full ancestor chain loaded.

        Args:
            session (AsyncSession): Active async session.
            pk (int | str): Primary key value.
            pk_column_name (str): Attribute name of the PK column on the model.
            filters (list[ColumnElement[bool]] | list[dict[str, Any]] | None, optional): Extra WHERE
                clauses merged with ``base_filters``. Defaults to None.

        Returns:
            Category: The matching ORM instance with ``parent`` populated
                recursively.

        """
        # Load all parent levels recursively (unlimited depth)
        stmt = (
            select(Category)
            .options(selectinload(Category.parent, recursion_depth=-1))
            .where(getattr(Category, pk_column_name) == pk)
        )

        if c_filters := self.concat_filters(filters):
            stmt = stmt.where(*c_filters)

        if self.select_in_options_single:
            stmt = stmt.options(*map(selectinload, self.select_in_options_single))

        result = await session.execute(stmt)
        return result.scalar_one()
