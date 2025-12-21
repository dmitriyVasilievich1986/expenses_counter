"""Base DAO module."""

__all__ = ("BaseDAO",)

from abc import ABC, abstractmethod
from typing import Generic, Type, TypeVar

from loguru import logger
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from expenses_counter.services.database.models.base import Base
from expenses_counter.services.database import DatabaseClient

B = TypeVar("B", bound=Type[Base])
T = TypeVar("T", bound=Type[BaseModel])
C = TypeVar("C", bound=Type[BaseModel])
U = TypeVar("U", bound=Type[BaseModel])
M = TypeVar("M", bound=Type[BaseModel])


class BaseDAO(ABC, Generic[B, T, C, U, M]):
    """Abstract base class for Data Access Objects (DAOs).

    This class defines the standard interface for CRUD operations that all
    DAO implementations must provide. It uses generic type parameters to
    ensure type safety across different DAO implementations.

    Type Parameters:
        B: Instance model type.
        T: The domain model type returned by DAO methods.
        C: The Pydantic model type used for creating new entities.
        U: The Pydantic model type used for full updates (PUT operations).
        M: The Pydantic model type used for partial updates (PATCH operations).
    """

    schema_cls: T

    def __init__(self, database_client: DatabaseClient):
        """Initialize the BaseDAO with a database client.

        Args:
            database_client: The database client used for database operations.

        """
        self.database_client = database_client

    @abstractmethod
    async def get_instance_by_id(self, pk: int, session: AsyncSession) -> B | None:
        """Retrieve a database instance by its primary key.

        This method should be implemented by subclasses to fetch a single
        database model instance based on its primary key. It operates within
        the provided database session.

        Args:
            pk: The primary key of the entity to retrieve.
            session: The async database session to use for the query.

        Returns:
            The database model instance if found, None otherwise.

        """
        pass

    @abstractmethod
    async def get_all_instances(self, session: AsyncSession) -> list[B]:
        """Retrieve all database instances of this type.

        This method should be implemented by subclasses to fetch all
        database model instances of the entity type. It operates within
        the provided database session.

        Args:
            session: The async database session to use for the query.

        Returns:
            A list of all database model instances.

        """
        pass

    async def get_by_id(self, pk: int) -> T | None:
        """Retrieve an entity by its primary key.

        Args:
            pk: The primary key of the entity to retrieve.

        Returns:
            The entity if found, None otherwise.

        """
        async with self.database_client.session_factory() as session:
            if (instance := await self.get_instance_by_id(pk, session)) is None:
                logger.debug(f"Instance not found: {pk}")
                return None
            payload = self.schema_cls.model_validate(instance)
            logger.debug(f"Instance found: {payload}")
            return payload

    async def get_all(self) -> list[T]:
        """Retrieve all entities of this type.

        Returns:
            A list of all entities.

        """
        async with self.database_client.session_factory() as session:
            instances = await self.get_all_instances(session)
            payload = [self.schema_cls.model_validate(instance) for instance in instances]
            logger.debug(f"Instances found: {payload}")
            return payload

    @abstractmethod
    async def create(self, obj: C) -> T:
        """Create a new entity.

        Args:
            obj: A Pydantic model containing the data for the new entity.

        Returns:
            The created entity.

        """
        pass

    @abstractmethod
    async def update(self, pk: int, obj: U) -> T:
        """Perform a full update on an entity.

        Args:
            pk: The primary key of the entity to update.
            obj: A Pydantic model containing all fields for the update.

        Returns:
            The updated entity.

        """
        pass

    @abstractmethod
    async def modify(self, pk: int, obj: M) -> T:
        """Perform a partial update on an entity.

        Args:
            pk: The primary key of the entity to modify.
            obj: A Pydantic model containing only the fields to update.

        Returns:
            The modified entity.

        """
        pass

    async def delete(self, pk: int) -> bool:
        """Delete an entity by its primary key.

        Args:
            pk: The primary key of the entity to delete.

        Returns:
            True if the entity was deleted, False otherwise.

        """
        async with self.database_client.session_factory() as session:
            if (instance := await self.get_instance_by_id(pk, session)) is None:
                logger.debug(f"Instance not found: {pk}")
                return False

            await session.delete(instance)
            await session.commit()
            logger.debug(f"Instance deleted: {pk}")
            return True
