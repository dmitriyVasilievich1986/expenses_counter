"""Transaction DAO module."""

__all__ = ("TransactionDAO",)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from expenses_counter.services.daos.base import BaseDAO
from expenses_counter.services.database.models.transaction import Transaction


class TransactionDAO(BaseDAO[Transaction]):
    """Data Access Object for Transaction entities.

    This DAO implements CRUD operations for Transaction entities, interacting with
    the database through the provided database client. It extends BaseDAO with
    transaction-specific implementations.
    """

    database_model = Transaction
    get_all_columns = (
        Transaction.id,
        Transaction.date,
        Transaction.count,
        Transaction.price,
        Transaction.product_id,
        Transaction.address_id,
    )

    async def _get_by_id_raw(self, session: AsyncSession, pk: int) -> Transaction:
        """Retrieve a single Transaction record by its primary key with relationships loaded.

        This is a raw method that works within an existing session context.
        It eagerly loads the associated product and address relationships to avoid N+1 queries.

        Args:
            session: The active database session.
            pk: The primary key of the transaction to retrieve.

        Returns:
            The Transaction model instance, or None if not found.

        """
        stmt = (
            select(Transaction)
            .options(selectinload(Transaction.product), selectinload(Transaction.address))
            .where(Transaction.id == pk)
        )
        result = await session.execute(stmt)
        return result.scalar()
