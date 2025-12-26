"""Dependency provider for category DAO."""

__all__ = ("get_category",)

from typing import Annotated

from fastapi import Depends

from expenses_counter.modules.middlewares.dependencies.get_db import get_db
from expenses_counter.services.daos import CategoryDAO
from expenses_counter.services.database import DatabaseClient


def get_category(
    db: Annotated[DatabaseClient, Depends(get_db)],
) -> CategoryDAO:
    """Dependency function that provides a singleton instance of CategoryDAO.

    Args:
        db: The database client.

    Returns:
        A CategoryDAO instance.

    """
    return CategoryDAO(database_client=db)
