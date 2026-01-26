"""Address DAO module."""

__all__ = ("AddressDAO",)

from sqlalchemy import select
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
    select_in_options_single = (Address.shop,)

    async def get_by_address(self, address: str) -> Address:
        """Get address by address string.

        Args:
            address: Address string to look up

        Returns:
            Address object matching the provided address string

        Raises:
            ValueError: If the address is not found in the database

        """
        stmt = select(Address).where(Address.address == address)

        if self.select_in_options_single:
            stmt = stmt.options(*map(selectinload, self.select_in_options_single))

        async with self.database_client.session_factory() as session:
            result = await session.execute(stmt)
            return result.scalar()
