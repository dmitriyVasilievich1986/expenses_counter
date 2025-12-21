"""Dependency provider for transaction DAO."""

__all__ = ("get_transaction",)

from typing import Annotated

from fastapi import Depends

from expenses_counter.services.daos import TransactionDAO
from expenses_counter.modules.middlewares.dependencies.get_db import get_db
from expenses_counter.services.database import DatabaseClient


def get_transaction(
    db: Annotated[DatabaseClient, Depends(get_db)],
) -> TransactionDAO:
    """Dependency function that provides a singleton instance of TransactionDAO.

    Args:
        db: The database client.

    Returns:
        A TransactionDAO instance.

    """
    return TransactionDAO(database_client=db)

