"""Dependency provider for user DAO."""

__all__ = ("get_user_dao",)

from typing import Annotated

from fastapi import Depends

from expenses_counter.modules.middlewares.dependencies.get_db import get_db
from expenses_counter.services.daos import UserDAO
from expenses_counter.services.database import AsyncDatabaseClient


def get_user_dao(
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> UserDAO:
    """Provide a ``UserDAO`` bound to the request-scoped database client.

    Args:
        db (AsyncDatabaseClient): Database client injected by FastAPI via ``get_db``.

    Returns:
        UserDAO: Data access layer for users using ``db``.

    """
    return UserDAO(database_client=db)
