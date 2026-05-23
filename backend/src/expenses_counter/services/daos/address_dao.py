"""Address DAO module."""

__all__ = ("AddressDAO",)


from expenses_counter.services.daos.base import BaseDAO, FilterType
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

    async def get_by_address(self, address: str, filters: FilterType = None) -> Address:
        """Load one address row by its ``address`` column value.

        Args:
            address (str): Value of the ``address`` column to match.
            filters (FilterType, optional): Extra WHERE
                clauses merged with ``base_filters``. Defaults to None.

        Returns:
            Address: The matching ORM instance.

        """
        if self.session is not None:
            return await self._get_by_pk_raw(self.session, address, "address", filters)

        async with self.database_client.session_factory() as session:  # type: ignore[union-attr]
            return await self._get_by_pk_raw(session, address, "address", filters)
