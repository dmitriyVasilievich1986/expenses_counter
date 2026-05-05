"""Product DAO module."""

__all__ = ("ProductDAO",)

from typing import Any

from sqlalchemy.sql import ColumnElement

from expenses_counter.services.daos.base import BaseDAO
from expenses_counter.services.database.models.product import Product


class ProductDAO(BaseDAO[Product]):
    """Data access for ``Product`` rows with optional ``category`` eager load."""

    database_model = Product
    get_all_columns = (Product.id, Product.name, Product.description, Product.category_id)
    select_in_options_single = (Product.category,)

    async def get_by_name(
        self, name: str, filters: list[ColumnElement[bool] | dict[str, Any]] | None = None
    ) -> Product:
        """Load one product row by its ``name`` column value.

        Args:
            name (str): Value of the ``name`` column to match.
            filters (list[ColumnElement[bool] | dict[str, Any]] | None, optional): Extra WHERE
                clauses merged with ``base_filters``. Defaults to None.

        Returns:
            Product: The matching ORM instance.

        """
        if self.session is not None:
            return await self._get_by_pk_raw(self.session, name, "name", filters)

        async with self.database_client.session_factory() as session:  # type: ignore[union-attr]
            return await self._get_by_pk_raw(session, name, "name", filters)
