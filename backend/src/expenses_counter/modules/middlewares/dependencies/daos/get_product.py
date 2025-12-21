"""Dependency provider for product DAO."""

__all__ = ("get_product",)

from typing import Annotated

from fastapi import Depends

from expenses_counter.services.daos import ProductDAO
from expenses_counter.modules.middlewares.dependencies.get_db import get_db
from expenses_counter.services.database import DatabaseClient


def get_product(
    db: Annotated[DatabaseClient, Depends(get_db)],
) -> ProductDAO:
    """Dependency function that provides a singleton instance of ProductDAO.

    Args:
        db: The database client.

    Returns:
        A ProductDAO instance.

    """
    return ProductDAO(database_client=db)
