"""Base DAO module."""

__all__ = ("BaseDAO",)

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

from expenses_counter.services.database import DatabaseClient

T = TypeVar("T")
C = TypeVar("C", bound=BaseModel)
U = TypeVar("U", bound=BaseModel)
M = TypeVar("M", bound=BaseModel)


class BaseDAO(ABC, Generic[T, C, U, M]):
    """Abstract base class for Data Access Objects (DAOs).

    This class defines the standard interface for CRUD operations that all
    DAO implementations must provide. It uses generic type parameters to
    ensure type safety across different DAO implementations.

    Type Parameters:
        T: The domain model type returned by DAO methods.
        C: The Pydantic model type used for creating new entities.
        U: The Pydantic model type used for full updates (PUT operations).
        M: The Pydantic model type used for partial updates (PATCH operations).
    """

    def __init__(self, database_client: DatabaseClient):
        """Initialize the BaseDAO with a database client.

        Args:
            database_client: The database client used for database operations.

        """
        self.database_client = database_client

    @abstractmethod
    async def get_by_id(self, pk: int) -> T | None:
        """Retrieve an entity by its primary key.

        Args:
            pk: The primary key of the entity to retrieve.

        Returns:
            The entity if found, None otherwise.

        """
        pass

    @abstractmethod
    async def get_all(self) -> list[T]:
        """Retrieve all entities of this type.

        Returns:
            A list of all entities.

        """
        pass

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

    @abstractmethod
    async def delete(self, pk: int) -> bool:
        """Delete an entity by its primary key.

        Args:
            pk: The primary key of the entity to delete.

        Returns:
            True if the entity was deleted, False otherwise.

        """
        pass
