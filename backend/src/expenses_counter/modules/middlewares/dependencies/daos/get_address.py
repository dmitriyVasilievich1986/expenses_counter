"""Dependency provider for shop DAO."""

__all__ = ("get_address",)

from typing import Annotated

from fastapi import Depends

from expenses_counter.modules.middlewares.dependencies.get_db import get_db
from expenses_counter.services.daos import AddressDAO
from expenses_counter.services.database import DatabaseClient


def get_address(
    db: Annotated[DatabaseClient, Depends(get_db)],
) -> AddressDAO:
    """Dependency function that provides a singleton instance of AddressDAO.

    Args:
        db: The database client.

    Returns:
        A AddressDAO instance.

    """
    return AddressDAO(database_client=db)
