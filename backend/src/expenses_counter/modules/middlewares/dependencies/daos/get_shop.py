"""Dependency provider for shop DAO."""

__all__ = ("get_shop",)

from typing import Annotated

from fastapi import Depends

from expenses_counter.daos import ShopDAO
from expenses_counter.modules.middlewares.dependencies.get_db import get_db
from expenses_counter.services.database import DatabaseClient


def get_shop(
    db: Annotated[DatabaseClient, Depends(get_db)],
) -> ShopDAO:
    """Dependency function that provides a singleton instance of ShopDAO.

    Args:
        db: The database client.

    Returns:
        A ShopDAO instance.

    """
    return ShopDAO(database_client=db)
