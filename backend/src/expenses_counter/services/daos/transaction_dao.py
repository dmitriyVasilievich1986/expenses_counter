"""Transaction DAO module."""

__all__ = ("TransactionDAO",)


from sqlalchemy import func, select

from expenses_counter.services.daos.base import BaseDAO
from expenses_counter.services.database.models.product import Product
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

    @BaseDAO.error_handler
    async def get_spendings_grouped_by_month(self) -> list[tuple[str, float]]:
        """Get the spendings grouped by month.

        Returns:
            A list of tuples containing the month (YYYY-MM format) and the spendings.

        """
        month_column = func.to_char(Transaction.date, "YYYY-MM-01")
        stmt = select(month_column, func.sum(Transaction.price)).group_by(month_column).order_by(month_column)
        result = await self.session.execute(stmt)
        return result.all()

    @BaseDAO.error_handler
    async def get_most_poular_products(self, limit: int = 10) -> list[Product]:
        """Get the most popular products.

        Args:
            limit: The number of products to return.

        Returns:
            A list of products.

        """
        amount = func.count(Transaction.product_id)
        subquery = (
            select(Transaction.product_id)
            .group_by(Transaction.product_id)
            .order_by(amount.desc())
            .limit(limit)
            .subquery()
        )
        stmt = select(Product).where(Product.id.in_(select(subquery.c.product_id)))
        result = await self.session.execute(stmt)
        return result.scalars().all()
