"""Shop DAO module."""

__all__ = ("ShopDAO",)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from expenses_counter.services.daos.base import BaseDAO
from expenses_counter.services.database.models.shop import Shop


class ShopDAO(BaseDAO[Shop]):
    """Data Access Object for Shop entities.

    This DAO implements CRUD operations for Shop entities, interacting with
    the database through the provided database client. It extends BaseDAO with
    shop-specific implementations.
    """

    database_model = Shop
    get_all_columns = (Shop.id, Shop.name)

    async def _get_by_id_raw(self, session: AsyncSession, pk: int) -> Shop:
        """Retrieve a single Shop record by its primary key with category relationship loaded.

        This is a raw method that works within an existing session context.
        It eagerly loads the associated category relationship to avoid N+1 queries.

        Args:
            session: The active database session.
            pk: The primary key of the shop to retrieve.

        Returns:
            The Shop model instance, or None if not found.

        """
        stmt = select(Shop).options(selectinload(Shop.category)).where(Shop.id == pk)
        result = await session.execute(stmt)
        return result.scalar()
