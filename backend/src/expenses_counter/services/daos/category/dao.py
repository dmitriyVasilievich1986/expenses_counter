"""Category DAO module."""

__all__ = ("CategoryDAO",)

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from expenses_counter.services.daos.base import BaseDAO
from expenses_counter.models.category import Category

from .schemas import CategoryGet, CategoryPatch, CategoryPost, CategoryPut


class CategoryDAO(BaseDAO[Category, CategoryGet, CategoryPost, CategoryPut, CategoryPatch]):
    """Data Access Object for Category entities.

    This DAO implements CRUD operations for Category entities, interacting with
    the database through the provided database client. It extends BaseDAO with
    category-specific implementations.
    """

    schema_cls = CategoryGet

    async def get_instance_by_id(self, pk: int, session: AsyncSession) -> Category | None:
        """Retrieve a category by its primary key.

        Args:
            pk: The primary key (ID) of the category to retrieve.
            session: The async database session to use for the query.

        Returns:
            A CategoryGet schema instance if found, None otherwise.

        """
        result = await session.execute(select(Category).where(Category.id == pk).options(joinedload(Category.parent)))
        return result.scalar_one_or_none()

    async def get_all_instances(self, session: AsyncSession) -> list[Category]:
        """Retrieve all categories.

        Args:
            session: The async database session to use for the query.

        Returns:
            A list of CategoryGet schema instances for all categories.

        """
        result = await session.execute(select(Category).options(joinedload(Category.parent)))
        return result.scalars().all()

    async def create(self, category: CategoryPost) -> CategoryGet:
        """Create a new category.

        Args:
            category: A CategoryPost schema instance containing the category data.

        Returns:
            A CategoryGet schema instance representing the created category.

        """
        logger.debug(f"Creating category: {category}")
        async with self.database_client.session_factory() as session:
            if (await self.get_instance_by_id(category.parent_id, session)) is None:
                logger.error(f"Parent category with id {category.parent_id} not found")
                raise ValueError(f"Parent category with id {category.parent_id} not found")

            new_category = Category(
                name=category.name,
                description=category.description,
                parent_id=category.parent_id,
            )
            session.add(new_category)
            await session.commit()

            payload = await self.get_by_id(new_category.id)
            logger.debug(f"Category created: {payload.id}")
            return payload

    async def update(self, pk: int, category: CategoryPut) -> CategoryGet:
        """Perform a full update on a category.

        Args:
            pk: The primary key (ID) of the category to update.
            category: A CategoryPut schema instance containing all fields for the update.

        Returns:
            A CategoryGet schema instance representing the updated category.

        Raises:
            ValueError: If the category with the given ID is not found.

        """
        logger.debug(f"Updating category with id {pk}: {category}")
        async with self.database_client.session_factory() as session:
            if (existing_category := await self.get_instance_by_id(pk, session)) is None:
                logger.error(f"Category with id {pk} not found")
                raise ValueError(f"Category with id {pk} not found")

            if category.parent_id and (await self.get_instance_by_id(category.parent_id, session)) is None:
                logger.error(f"Parent category with id {category.parent_id} not found")
                raise ValueError(f"Parent category with id {category.parent_id} not found")

            existing_category.parent_id = category.parent_id
            existing_category.name = category.name
            existing_category.description = category.description

            await session.commit()
            payload = await self.get_by_id(existing_category.id)
            logger.debug(f"Category updated: {payload.id}")
            return payload

    async def modify(self, pk: int, category: CategoryPatch) -> CategoryGet:
        """Perform a partial update on a category.

        Only the fields provided in the CategoryPatch schema will be updated.
        Fields that are None will be left unchanged.

        Args:
            pk: The primary key (ID) of the category to modify.
            category: A CategoryPatch schema instance containing only the fields to update.

        Returns:
            A CategoryGet schema instance representing the modified category.

        Raises:
            ValueError: If the category with the given ID is not found.

        """
        logger.debug(f"Modifying category with id {pk}: {category}")
        async with self.database_client.session_factory() as session:
            if (existing_category := await self.get_instance_by_id(pk, session)) is None:
                raise ValueError(f"Category with id {pk} not found")

            if category.name is not None:
                existing_category.name = category.name
            if category.description is not None:
                existing_category.description = category.description
            if category.parent_id:
                if (await self.get_instance_by_id(category.parent_id, session)) is None:
                    logger.error(f"Parent category with id {category.parent_id} not found")
                    raise ValueError(f"Parent category with id {category.parent_id} not found")
                existing_category.parent_id = category.parent_id

            await session.commit()
            payload = await self.get_by_id(existing_category.id)
            logger.debug(f"Category modified: {payload.id}")
            return payload
