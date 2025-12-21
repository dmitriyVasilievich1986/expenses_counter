"""Address DAO module."""

__all__ = ("AddressDAO",)

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from expenses_counter.services.daos.base import BaseDAO
from expenses_counter.services.daos.shop.dao import ShopDAO
from expenses_counter.services.database.models.address import Address

from .schemas import AddressGet, AddressPatch, AddressPost, AddressPut


class AddressDAO(BaseDAO[Address, AddressGet, AddressPost, AddressPut, AddressPatch]):
    """Data Access Object for Address entities.

    This DAO implements CRUD operations for Address entities, interacting with
    the database through the provided database client. It extends BaseDAO with
    address-specific implementations.
    """

    schema_cls = AddressGet

    async def get_instance_by_id(self, pk: int, session: AsyncSession) -> Address | None:
        """Retrieve an address by its primary key.

        Args:
            pk: The primary key (ID) of the address to retrieve.
            session: The async database session to use for the query.

        Returns:
            An Address instance if found, None otherwise.

        """
        result = await session.execute(select(Address).where(Address.id == pk).options(joinedload(Address.shop)))
        return result.scalar_one_or_none()

    async def get_all_instances(self, session: AsyncSession) -> list[Address]:
        """Retrieve all addresses.

        Args:
            session: The async database session to use for the query.

        Returns:
            A list of Address instances for all addresses.

        """
        result = await session.execute(select(Address).options(joinedload(Address.shop)))
        return result.scalars().all()

    async def create(self, address: AddressPost) -> AddressGet:
        """Create a new address.

        Args:
            address: An AddressPost schema instance containing the address data.

        Returns:
            An AddressGet schema instance representing the created address.

        """
        logger.debug(f"Creating address: {address}")
        async with self.database_client.session_factory() as session:
            shop_dao = ShopDAO(self.database_client)
            if (await shop_dao.get_instance_by_id(address.shop_id, session)) is None:
                logger.error(f"Shop with id {address.shop_id} not found")
                raise ValueError(f"Shop with id {address.shop_id} not found")

            new_address = Address(
                local_name=address.local_name,
                address=address.address,
                shop_id=address.shop_id,
            )
            session.add(new_address)
            await session.commit()

            payload = await self.get_by_id(new_address.id)
            logger.debug(f"Address created: {payload.id}")
            return payload

    async def update(self, pk: int, address: AddressPut) -> AddressGet:
        """Perform a full update on an address.

        Args:
            pk: The primary key (ID) of the address to update.
            address: An AddressPut schema instance containing all fields for the update.

        Returns:
            An AddressGet schema instance representing the updated address.

        Raises:
            ValueError: If the address with the given ID is not found or if the shop is not found.

        """
        logger.debug(f"Updating address with id {pk}: {address}")
        async with self.database_client.session_factory() as session:
            if (existing_address := await self.get_instance_by_id(pk, session)) is None:
                logger.error(f"Address with id {pk} not found")
                raise ValueError(f"Address with id {pk} not found")

            shop_dao = ShopDAO(self.database_client)
            if (await shop_dao.get_instance_by_id(address.shop_id, session)) is None:
                logger.error(f"Shop with id {address.shop_id} not found")
                raise ValueError(f"Shop with id {address.shop_id} not found")

            existing_address.shop_id = address.shop_id
            existing_address.local_name = address.local_name
            existing_address.address = address.address

            await session.commit()
            payload = await self.get_by_id(existing_address.id)
            logger.debug(f"Address updated: {payload.id}")
            return payload

    async def modify(self, pk: int, address: AddressPatch) -> AddressGet:
        """Perform a partial update on an address.

        Only the fields provided in the AddressPatch schema will be updated.
        Fields that are None will be left unchanged.

        Args:
            pk: The primary key (ID) of the address to modify.
            address: An AddressPatch schema instance containing only the fields to update.

        Returns:
            An AddressGet schema instance representing the modified address.

        Raises:
            ValueError: If the address with the given ID is not found or if the shop is not found.

        """
        logger.debug(f"Modifying address with id {pk}: {address}")
        async with self.database_client.session_factory() as session:
            if (existing_address := await self.get_instance_by_id(pk, session)) is None:
                raise ValueError(f"Address with id {pk} not found")

            if address.local_name is not None:
                existing_address.local_name = address.local_name
            if address.address is not None:
                existing_address.address = address.address
            if address.shop_id is not None:
                shop_dao = ShopDAO(self.database_client)
                if (await shop_dao.get_instance_by_id(address.shop_id, session)) is None:
                    logger.error(f"Shop with id {address.shop_id} not found")
                    raise ValueError(f"Shop with id {address.shop_id} not found")
                existing_address.shop_id = address.shop_id

            await session.commit()
            payload = await self.get_by_id(existing_address.id)
            logger.debug(f"Address modified: {payload.id}")
            return payload
