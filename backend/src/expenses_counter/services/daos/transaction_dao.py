"""Async DAO for transactions and derived spending or popularity queries."""

__all__ = ("TransactionDAO",)


from typing import Sequence

from sqlalchemy import func, Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import ColumnElement

from expenses_counter.services.daos.base import BaseDAO
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
        filters: list[ColumnElement[bool]] | None,
    ) -> Sequence[tuple[str, float]]:
        """Sum transaction prices grouped by calendar month.

        Uses dialect-specific date truncation: ``strftime`` on SQLite and
        ``to_char`` on PostgreSQL.

        Args:
            session (AsyncSession): Active async session.
            filters (list[ColumnElement[bool]] | None, optional): Extra WHERE
                clauses merged with ``base_filters``. Defaults to None.

        Returns:
            Sequence[tuple[str, float]]: Pairs of month label (``YYYY-MM-01``)
                and total spending for that month, ordered chronologically.

        """
        if session.bind.dialect.name == "sqlite":
            date_column = func.strftime("%Y-%m-01", Transaction.date)
        else:
            date_column = func.to_char(Transaction.date, "YYYY-MM-01")

        filters_ = self.concat_filters(self.base_filters, filters)
        stmt = (
            select(date_column, func.sum(Transaction.price))
            .group_by(date_column)
            .order_by(date_column)
            .where(*filters_)
        )
        result = await session.execute(stmt)
        return result.tuples().all()

    async def get_spendings_grouped_by_month(
        self, filters: list[ColumnElement[bool]] | None = None
    ) -> Sequence[tuple[str, float]]:
        """Return monthly spending totals using injected or factory-opened session.

        Args:
            filters (list[ColumnElement[bool]] | None, optional): Extra WHERE
                clauses merged with ``base_filters``. Defaults to None.

        Returns:
            Sequence[tuple[str, float]]: Pairs of month label (``YYYY-MM-01``)
                and total spending for that month, ordered chronologically.

        """
        if self.session is not None:
            return await self._get_spendings_grouped_by_month_raw(self.session, filters)

        async with self.database_client.session_factory() as session:  # type: ignore[union-attr]
            return await self._get_spendings_grouped_by_month_raw(session, filters)

    async def _get_most_popular_products_raw(
        self,
        session: AsyncSession,
        limit: int | None,
        filters: list[ColumnElement[bool]] | None,
    ) -> Sequence[Product]:
        """Load products ranked by how often they appear in transactions.

        Args:
            session (AsyncSession): Active async session.
            limit (int | None): Maximum number of product IDs to consider;
                None returns all ranked products.
            filters (list[ColumnElement[bool]] | None, optional): Extra WHERE
                clauses merged with ``base_filters``. Defaults to None.

        Returns:
            Sequence[Product]: ``Product`` rows for the top-ranked IDs, in
                descending transaction-count order.

        """
        amount = func.count(Transaction.product_id)
        ranked: Select[tuple[int, int]] = select(
            Transaction.product_id,
            amount.label("transaction_count"),
        ).group_by(Transaction.product_id)
        if c_filters := self.concat_filters(self.base_filters, filters):
            ranked = ranked.where(*c_filters)
        ranked = ranked.order_by(amount.desc())
        if limit:
            ranked = ranked.limit(limit)

        ranked_sq = ranked.subquery()
        stmt = (
            select(Product)
            .join(ranked_sq, Product.id == ranked_sq.c.product_id)
            .order_by(ranked_sq.c.transaction_count.desc())
        )

        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_most_popular_products(
        self,
        limit: int = 10,
        filters: list[ColumnElement[bool]] | None = None,
    ) -> Sequence[Product]:
        """Return products most frequently referenced in transactions.

        Uses an injected session when present; otherwise opens a
        short-lived session from the bound database client.

        Args:
            limit (int, optional): Maximum number of products to return.
                Defaults to 10.
            filters (list[ColumnElement[bool]] | None, optional): Extra WHERE
                clauses merged with ``base_filters``. Defaults to None.

        Returns:
            Sequence[Product]: ``Product`` rows for the top-ranked IDs, in
                descending transaction-count order.

        """
        if self.session is not None:
            return await self._get_most_popular_products_raw(self.session, limit, filters)

        async with self.database_client.session_factory() as session:  # type: ignore[union-attr]
            return await self._get_most_popular_products_raw(session, limit, filters)
