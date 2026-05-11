"""Async DAO for transactions and derived spending or popularity queries."""

__all__ = ("TransactionDAO",)


from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from expenses_counter.services.daos.base import BaseDAO
from expenses_counter.services.database.models.product import Product
from expenses_counter.services.database.models.transaction import Transaction


class TransactionDAO(BaseDAO[Transaction]):
    """Data access for ``Transaction`` with ``product`` and ``address`` eager loads."""

    database_model = Transaction
    select_in_options_single = (Transaction.product, Transaction.address)
    select_in_options_all = (Transaction.product, Transaction.address)

    async def _get_spendings_grouped_by_month_raw(self, session: AsyncSession) -> Sequence[tuple[str, float]]:
        """Sum transaction prices grouped by calendar month using the given session.

        Month keys are normalized to the first day of each month as ``YYYY-MM-01``.
        SQLite uses ``strftime``; other dialects use ``to_char`` for grouping.

        Args:
            session (AsyncSession): Session used to run the aggregation query.

        Returns:
            Sequence[tuple[str, float]]: Pairs of month key and total spending for that month,
                ordered by month ascending.

        """
        if session.bind.dialect.name == "sqlite":
            date_column = func.strftime("%Y-%m-01", Transaction.date)
        else:
            date_column = func.to_char(Transaction.date, "YYYY-MM-01")

        stmt = select(date_column, func.sum(Transaction.price)).group_by(date_column).order_by(date_column)
        result = await session.execute(stmt)
        return result.tuples().all()

    async def get_spendings_grouped_by_month(self) -> Sequence[tuple[str, float]]:
        """Return total spending per month across all transactions.

        Uses ``self.session`` when the DAO was constructed with an active session;
        otherwise opens a short-lived session from ``database_client``.

        Returns:
            Sequence[tuple[str, float]]: Month keys (``YYYY-MM-01``) and summed prices,
                ordered by month ascending.

        """
        if self.session is not None:
            return await self._get_spendings_grouped_by_month_raw(self.session)

        async with self.database_client.session_factory() as session:  # type: ignore[union-attr]
            return await self._get_spendings_grouped_by_month_raw(session)

    async def get_most_popular_products(self, limit: int = 10) -> Sequence[Product]:
        """Return products ranked by how often they appear in transactions.

        Args:
            limit (int, optional): Maximum number of products to return.
                Defaults to 10.

        Returns:
            Sequence[Product]: Products with the highest transaction counts,
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

        async with self.database_client.session_factory() as session:  # type: ignore[union-attr]
            result = await session.execute(stmt)
            return result.scalars().all()
