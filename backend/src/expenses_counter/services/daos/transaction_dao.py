"""Transaction DAO module."""

__all__ = ("TransactionDAO",)


from expenses_counter.services.daos.base import BaseDAO
from expenses_counter.services.database.models.transaction import Transaction


class TransactionDAO(BaseDAO[Transaction]):
    """Data Access Object for Transaction entities.

    This DAO implements CRUD operations for Transaction entities, interacting with
    the database through the provided database client. It extends BaseDAO with
    transaction-specific implementations.
    """

    database_model = Transaction
    select_in_options_single = (Transaction.product, Transaction.address)
    select_in_options_all = (Transaction.product, Transaction.address)
