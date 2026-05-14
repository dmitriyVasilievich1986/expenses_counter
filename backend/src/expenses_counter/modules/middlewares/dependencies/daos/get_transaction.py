"""Dependency provider for transaction DAO."""

__all__ = ("get_transaction",)

from typing import Annotated

from fastapi import Depends

from expenses_counter.modules.middlewares.dependencies.get_db import get_db
from expenses_counter.modules.middlewares.dependencies.user_authorized import user_authorized
from expenses_counter.services.daos import TransactionDAO
from expenses_counter.services.database import AsyncDatabaseClient
from expenses_counter.services.database.models.user import User


def get_transaction(
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
    user: Annotated[User, Depends(user_authorized)],
) -> TransactionDAO:
    """Dependency function that provides a singleton instance of TransactionDAO.

    Args:
        db: The database client.
        user: The user who is authorized to access the transactions.

    Returns:
        A TransactionDAO instance.

    """
    return TransactionDAO(database_client=db, user=user)
