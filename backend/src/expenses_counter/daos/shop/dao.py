"""Shop DAO module."""

__all__ = ("ShopDAO",)

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from expenses_counter.daos.base import BaseDAO
from expenses_counter.daos.category.dao import CategoryDAO
from expenses_counter.models.shop import Shop

from .schemas import ShopGet, ShopPatch, ShopPost, ShopPut


class ShopDAO(BaseDAO[Shop, ShopGet, ShopPost, ShopPut, ShopPatch]):
    """Data Access Object for Shop entities.

    This DAO implements CRUD operations for Shop entities, interacting with
    the database through the provided database client. It extends BaseDAO with
    shop-specific implementations.
    """

    schema_cls = ShopGet

    async def get_instance_by_id(self, pk: int, session: AsyncSession) -> Shop | None:
        """Retrieve a shop by its primary key.

        Args:
            pk: The primary key (ID) of the shop to retrieve.
            session: The async database session to use for the query.

        Returns:
            A ShopGet schema instance if found, None otherwise.

        """
        result = await session.execute(
            select(Shop).where(Shop.id == pk).options(joinedload(Shop.category))
        )
        return result.scalar_one_or_none()

    async def get_all_instances(self, session: AsyncSession) -> list[Shop]:
        """Retrieve all shops.

        Args:
            session: The async database session to use for the query.

        Returns:
            A list of ShopGet schema instances.

        """
        result = await session.execute(select(Shop).options(joinedload(Shop.category)))
        return result.scalars().all()

    async def create(self, shop: ShopPost) -> ShopGet:
        """Create a new shop.

        Args:
            shop: A ShopPost schema instance containing the shop data.

        Returns:
            A ShopGet schema instance representing the created shop.

        """
        logger.debug(f"Creating shop: {shop}")
        category_dao = CategoryDAO(self.database_client)

        async with self.database_client.session_factory() as session:
            if (
                shop.category_id
                and (await category_dao.get_instance_by_id(shop.category_id, session))
                is None
            ):
                logger.error(f"Category with id {shop.category_id} not found")
                raise ValueError(f"Category with id {shop.category_id} not found")

            new_shop = Shop(
                name=shop.name,
                icon=shop.icon,
                description=shop.description,
                category_id=shop.category_id,
            )
            session.add(new_shop)
            await session.commit()

            payload = await self.get_by_id(new_shop.id)
            logger.debug(f"Shop created: {payload}")
            return payload

    async def update(self, pk: int, shop: ShopPut) -> ShopGet:
        """Update a shop by its primary key.

        Args:
            pk: The primary key (ID) of the shop to update.
            shop: A ShopPut schema instance containing the shop data.

        Returns:
            A ShopGet schema instance representing the updated shop.

        """
        logger.debug(f"Updating shop with id {pk}: {shop}")
        category_dao = CategoryDAO(self.database_client)

        async with self.database_client.session_factory() as session:
            if (existing_shop := await self.get_instance_by_id(pk, session)) is None:
                logger.error(f"Shop with id {pk} not found")
                raise ValueError(f"Shop with id {pk} not found")

            if (
                shop.category_id
                and (await category_dao.get_instance_by_id(shop.category_id, session))
                is None
            ):
                logger.error(f"Category with id {shop.category_id} not found")
                raise ValueError(f"Category with id {shop.category_id} not found")

            existing_shop.name = shop.name
            existing_shop.icon = shop.icon
            existing_shop.description = shop.description
            existing_shop.category_id = shop.category_id
            await session.commit()

            payload = await self.get_by_id(existing_shop.id)
            logger.debug(f"Shop updated: {payload}")
            return payload

    async def modify(self, pk: int, shop: ShopPatch) -> ShopGet:
        """Modify a shop by its primary key.

        Args:
            pk: The primary key (ID) of the shop to modify.
            shop: A ShopPatch schema instance containing the shop data.

        Returns:
            A ShopGet schema instance representing the modified shop.

        """
        logger.debug(f"Modifying shop with id {pk}: {shop}")
        category_dao = CategoryDAO(self.database_client)

        async with self.database_client.session_factory() as session:
            if (existing_shop := await self.get_instance_by_id(pk, session)) is None:
                logger.error(f"Shop with id {pk} not found")
                raise ValueError(f"Shop with id {pk} not found")

            if (
                shop.category_id
                and (await category_dao.get_instance_by_id(shop.category_id, session))
                is None
            ):
                logger.error(f"Category with id {shop.category_id} not found")
                raise ValueError(f"Category with id {shop.category_id} not found")

            if shop.name is not None:
                existing_shop.name = shop.name
            if shop.icon is not None:
                existing_shop.icon = shop.icon
            if shop.description is not None:
                existing_shop.description = shop.description
            if shop.category_id is not None:
                existing_shop.category_id = shop.category_id
            await session.commit()

            payload = await self.get_by_id(existing_shop.id)
            logger.debug(f"Shop modified: {payload}")
            return payload
