"""Address DAO module."""

__all__ = ("AddressDAO",)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from expenses_counter.services.daos.base import BaseDAO
from expenses_counter.services.database.models.address import Address


class AddressDAO(BaseDAO[Address]):
    """Data Access Object for Address entities.

    This DAO implements CRUD operations for Address entities, interacting with
    the database through the provided database client. It extends BaseDAO with
    address-specific implementations.
    """

    database_model = Address
    get_all_columns = (Address.id, Address.local_name, Address.address)

    async def _get_by_id_raw(self, session: AsyncSession, pk: int) -> Address:
        stmt = select(Address).options(selectinload(Address.shop)).where(Address.id == pk)
        result = await session.execute(stmt)
        return result.scalar()
