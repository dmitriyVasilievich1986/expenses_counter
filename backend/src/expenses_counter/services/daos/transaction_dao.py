"""Async DAO for transactions and derived spending or popularity queries."""

__all__ = ("TransactionDAO",)


from sqlalchemy import func, select

from expenses_counter.services.daos.base import BaseDAO
from expenses_counter.services.database.models.product import Product
from expenses_counter.services.database.models.transaction import Transaction


class TransactionDAO(BaseDAO[Transaction]):
    """Data access for ``Transaction`` with ``product`` and ``address`` eager loads."""

    database_model = Transaction
    select_in_options_single = (Transaction.product, Transaction.address)
    select_in_options_all = (Transaction.product, Transaction.address)

    async def get_spendings_grouped_by_month(self) -> list[tuple[str, float]]:
        """Return total ``price`` per calendar month across all transactions.

        Returns:
            list[tuple[str, float]]: Pairs of month label (``YYYY-MM-01``) and
                summed spending for that month, ordered chronologically.

        """
        month_column = func.to_char(Transaction.date, "YYYY-MM-01")
        stmt = select(month_column, func.sum(Transaction.price)).group_by(month_column).order_by(month_column)

        if self.session is not None:
            result = await self.session.execute(stmt)
            return result.all()

        async with self.database_client.session_factory() as session:
            result = await session.execute(stmt)
            return result.all()

    async def get_most_popular_products(self, limit: int = 10) -> list[Product]:
        """Return products ranked by how often they appear in transactions.

        Args:
            limit (int, optional): Maximum number of products to return.
                Defaults to 10.

        Returns:
            list[Product]: Products with the highest transaction counts,
                most frequent first.

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

        if self.session is not None:
            result = await self.session.execute(stmt)
            return result.scalars().all()

        async with self.database_client.session_factory() as session:
            result = await session.execute(stmt)
            return result.scalars().all()
