"""Product DAO module."""

__all__ = ("ProductDAO",)

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from expenses_counter.services.daos.base import BaseDAO
from expenses_counter.services.daos.category import CategoryDAO
from expenses_counter.services.database.models.product import Product

from .schemas import ProductGet, ProductPatch, ProductPost, ProductPut


class ProductDAO(BaseDAO[Product, ProductGet, ProductPost, ProductPut, ProductPatch]):
    """Data Access Object for Product entities.

    This DAO implements CRUD operations for Product entities, interacting with
    the database through the provided database client. It extends BaseDAO with
    product-specific implementations.
    """

    schema_cls = ProductGet

    async def get_instance_by_id(self, pk: int, session: AsyncSession) -> Product | None:
        """Retrieve a product by its primary key.

        Args:
            pk: The primary key (ID) of the product to retrieve.
            session: The async database session to use for the query.

        Returns:
            A Product instance if found, None otherwise.

        """
        result = await session.execute(
            select(Product).where(Product.id == pk).options(joinedload(Product.sub_category))
        )
        return result.scalar_one_or_none()

    async def get_all_instances(self, session: AsyncSession) -> list[Product]:
        """Retrieve all products.

        Args:
            session: The async database session to use for the query.

        Returns:
            A list of Product instances for all products.

        """
        result = await session.execute(select(Product).options(joinedload(Product.sub_category)))
        return result.scalars().all()

    async def create(self, product: ProductPost) -> ProductGet:
        """Create a new product.

        Args:
            product: A ProductPost schema instance containing the product data.

        Returns:
            A ProductGet schema instance representing the created product.

        Raises:
            ValueError: If the sub_category_id is provided but the category does not exist.

        """
        logger.debug(f"Creating product: {product}")
        category_dao = CategoryDAO(self.database_client)

        async with self.database_client.session_factory() as session:
            if (
                product.sub_category_id
                and (await category_dao.get_instance_by_id(product.sub_category_id, session)) is None
            ):
                logger.error(f"Sub category with id {product.sub_category_id} not found")
                raise ValueError(f"Sub category with id {product.sub_category_id} not found")

            new_product = Product(
                name=product.name,
                description=product.description,
                sub_category_id=product.sub_category_id,
            )
            session.add(new_product)
            await session.commit()

            payload = await self.get_by_id(new_product.id)
            logger.debug(f"Product created: {payload.id}")
            return payload

    async def update(self, pk: int, product: ProductPut) -> ProductGet:
        """Perform a full update on a product.

        Args:
            pk: The primary key (ID) of the product to update.
            product: A ProductPut schema instance containing all fields for the update.

        Returns:
            A ProductGet schema instance representing the updated product.

        Raises:
            ValueError: If the product with the given ID is not found, or if the
                sub_category_id is provided but the category does not exist.

        """
        logger.debug(f"Updating product with id {pk}: {product}")
        category_dao = CategoryDAO(self.database_client)

        async with self.database_client.session_factory() as session:
            if (existing_product := await self.get_instance_by_id(pk, session)) is None:
                logger.error(f"Product with id {pk} not found")
                raise ValueError(f"Product with id {pk} not found")

            if (
                product.sub_category_id
                and (await category_dao.get_instance_by_id(product.sub_category_id, session)) is None
            ):
                logger.error(f"Sub category with id {product.sub_category_id} not found")
                raise ValueError(f"Sub category with id {product.sub_category_id} not found")

            existing_product.sub_category_id = product.sub_category_id
            existing_product.name = product.name
            existing_product.description = product.description

            await session.commit()
            payload = await self.get_by_id(existing_product.id)
            logger.debug(f"Product updated: {payload.id}")
            return payload

    async def modify(self, pk: int, product: ProductPatch) -> ProductGet:
        """Perform a partial update on a product.

        Only the fields provided in the ProductPatch schema will be updated.
        Fields that are None will be left unchanged.

        Args:
            pk: The primary key (ID) of the product to modify.
            product: A ProductPatch schema instance containing only the fields to update.

        Returns:
            A ProductGet schema instance representing the modified product.

        Raises:
            ValueError: If the product with the given ID is not found, or if the
                sub_category_id is provided but the category does not exist.

        """
        logger.debug(f"Modifying product with id {pk}: {product}")
        category_dao = CategoryDAO(self.database_client)

        async with self.database_client.session_factory() as session:
            if (existing_product := await self.get_instance_by_id(pk, session)) is None:
                raise ValueError(f"Product with id {pk} not found")

            if product.name is not None:
                existing_product.name = product.name
            if product.description is not None:
                existing_product.description = product.description
            if product.sub_category_id is not None:
                if (
                    product.sub_category_id
                    and (await category_dao.get_instance_by_id(product.sub_category_id, session)) is None
                ):
                    logger.error(f"Sub category with id {product.sub_category_id} not found")
                    raise ValueError(f"Sub category with id {product.sub_category_id} not found")
                existing_product.sub_category_id = product.sub_category_id

            await session.commit()
            payload = await self.get_by_id(existing_product.id)
            logger.debug(f"Product modified: {payload.id}")
            return payload
