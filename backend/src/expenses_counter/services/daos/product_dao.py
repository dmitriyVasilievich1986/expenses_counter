"""Product DAO module."""

__all__ = ("ProductDAO",)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from expenses_counter.services.daos.base import BaseDAO
from expenses_counter.services.database.models.product import Product


class ProductDAO(BaseDAO[Product]):
    """Data Access Object for Product entities.

    This DAO implements CRUD operations for Product entities, interacting with
    the database through the provided database client. It extends BaseDAO with
    product-specific implementations.
    """

    database_model = Product
    get_all_columns = (Product.id, Product.name)

    async def _get_by_id_raw(self, session: AsyncSession, pk: int) -> Product:
        """Retrieve a single Product record by its primary key with category relationship loaded.

        This is a raw method that works within an existing session context.
        It eagerly loads the associated category relationship to avoid N+1 queries.

        Args:
            session: The active database session.
            pk: The primary key of the product to retrieve.

        Returns:
            The Product model instance, or None if not found.

        """
        stmt = select(Product).options(selectinload(Product.category)).where(Product.id == pk)
        result = await session.execute(stmt)
        return result.scalar()
