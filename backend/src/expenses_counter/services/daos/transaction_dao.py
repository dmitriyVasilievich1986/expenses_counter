"""Async DAO for transactions and derived spending or popularity queries."""

__all__ = ("TransactionDAO",)


from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from expenses_counter.services.daos.base import BaseDAO, FilterType
from expenses_counter.services.database.models.product import Product
from expenses_counter.services.database.models.transaction import Transaction


class TransactionDAO(BaseDAO[Transaction]):
    """Data access for ``Transaction`` with ``product`` and ``address`` eager loads."""

    database_model = Transaction
    select_in_options_single = (Transaction.product, Transaction.address)
    select_in_options_all = (Transaction.product, Transaction.address)

    async def _get_spendings_grouped_by_month_raw(
        self,
        session: AsyncSession,
        filters: FilterType = None,
    ) -> Sequence[tuple[str, float]]:
        """Sum transaction prices grouped by calendar month.

        Uses dialect-specific date truncation: ``strftime`` on SQLite and
        ``to_char`` on PostgreSQL.

        Args:
            session (AsyncSession): Active async session.
            filters (FilterType, optional): Extra WHERE
                clauses merged with ``base_filters``. Defaults to None.

        Returns:
            Sequence[tuple[str, float]]: Pairs of month label (``YYYY-MM-01``)
                and total spending for that month, ordered chronologically.

        """
        if session.bind.dialect.name == "sqlite":
            date_column = func.strftime("%Y-%m-01", Transaction.date)
        else:
            date_column = func.to_char(Transaction.date, "YYYY-MM-01")

        filters_ = self.concat_filters(filters)
        stmt = (
            select(date_column, func.sum(Transaction.price))
            .group_by(date_column)
            .order_by(date_column)
            .where(*filters_)
        )
        result = await session.execute(stmt)
        return result.tuples().all()

    async def get_spendings_grouped_by_month(self, filters: FilterType = None) -> Sequence[tuple[str, float]]:
        """Return monthly spending totals using injected or factory-opened session.

        Args:
            filters (FilterType, optional): Extra WHERE
                clauses merged with ``base_filters``. Defaults to None.

        Returns:
            Sequence[tuple[str, float]]: Pairs of month label (``YYYY-MM-01``)
                and total spending for that month, ordered chronologically.

        """
        if self.session is not None:
            return await self._get_spendings_grouped_by_month_raw(self.session, filters)

        async with self.database_client.session_factory() as session:  # type: ignore[union-attr]
            return await self._get_spendings_grouped_by_month_raw(session, filters)

    async def get_most_popular_products(
        self,
        limit: int = 10,
        filters: FilterType = None,
    ) -> Sequence[Product]:
        """Return products ranked by how often they appear in transactions.

        Args:
            limit (int, optional): Maximum number of products to return.
                Defaults to 10.
            filters (FilterType, optional): Extra WHERE
                clauses applied to transactions before counting. Defaults to None.

        Returns:
            Sequence[Product]: Product rows for the most frequently purchased
                items, in descending order of transaction count.

        """
        filters_ = self.concat_filters(filters)
        amount = func.count(Transaction.product_id)
        subquery = (
            select(Transaction.product_id)
            .where(*filters_)
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
