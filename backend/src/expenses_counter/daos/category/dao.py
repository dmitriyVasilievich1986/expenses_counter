"""Category DAO module."""

__all__ = ("CategoryDAO",)

from sqlalchemy import select

from expenses_counter.daos.base import BaseDAO
from expenses_counter.models.category import Category

from .schemas import CategoryGet, CategoryPatch, CategoryPost, CategoryPut


class CategoryDAO(BaseDAO[CategoryGet, CategoryPost, CategoryPut, CategoryPatch]):
    """Data Access Object for Category entities.

    This DAO implements CRUD operations for Category entities, interacting with
    the database through the provided database client. It extends BaseDAO with
    category-specific implementations.
    """

    async def get_by_id(self, pk: int) -> CategoryGet | None:
        """Retrieve a category by its primary key.

        Args:
            pk: The primary key (ID) of the category to retrieve.

        Returns:
            A CategoryGet schema instance if found, None otherwise.

        """
        async for session in self.database_client.get_session():
            result = await session.execute(select(Category).where(Category.id == pk))
            if category := result.scalar_one_or_none():
                return CategoryGet.model_validate(category)
        return None

    async def get_all(self) -> list[CategoryGet]:
        """Retrieve all categories.

        Returns:
            A list of CategoryGet schema instances for all categories.

        """
        async for session in self.database_client.get_session():
            result = await session.execute(select(Category))
            return [
                CategoryGet.model_validate(category)
                for category in result.scalars().all()
            ]
        raise RuntimeError("Failed to get all categories")

    async def create(self, category: CategoryPost) -> CategoryGet:
        """Create a new category.

        Args:
            category: A CategoryPost schema instance containing the category data.

        Returns:
            A CategoryGet schema instance representing the created category.

        """
        async for session in self.database_client.get_session():
            new_category = Category(
                name=category.name,
                description=category.description,
                parent_id=category.parent_id,
            )
            session.add(new_category)
            await session.commit()
            return CategoryGet.model_validate(new_category)
        return None

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
        async for session in self.database_client.get_session():
            result = await session.execute(select(Category).where(Category.id == pk))
            if existing_category := result.scalar_one_or_none():
                existing_category.name = category.name
                existing_category.description = category.description
                existing_category.parent_id = category.parent_id
                await session.commit()
                return CategoryGet.model_validate(existing_category)
        raise ValueError(f"Category with id {pk} not found")

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
        async for session in self.database_client.get_session():
            result = await session.execute(select(Category).where(Category.id == pk))
            if existing_category := result.scalar_one_or_none():
                if category.name is not None:
                    existing_category.name = category.name
                if category.description is not None:
                    existing_category.description = category.description
                if category.parent_id is not None:
                    existing_category.parent_id = category.parent_id
                await session.commit()
                return CategoryGet.model_validate(existing_category)
        raise ValueError(f"Category with id {pk} not found")

    async def delete(self, pk: int) -> bool:
        """Delete a category by its primary key.

        Args:
            pk: The primary key (ID) of the category to delete.

        Returns:
            True if the category was deleted, False if it was not found.

        """
        async for session in self.database_client.get_session():
            result = await session.execute(select(Category).where(Category.id == pk))
            if category := result.scalar_one_or_none():
                await session.delete(category)
                await session.commit()
                return True
        return False
