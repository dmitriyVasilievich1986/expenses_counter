"""Unit tests for ``TransactionDAO`` filtered queries.

The DAO no longer holds user-scoping state in its constructor — instead the
route layer builds per-user filter clauses and passes them in explicitly.
These tests exercise the DAO directly against a real (SQLite) database via
the ``db_session`` fixture and verify that:

* ``get_all`` honours an explicit ``user_id`` filter for non-admin scopes.
* ``get_all`` without filters returns rows across users (admin view).
* ``get_by_pk`` rejects another user's row when scoped via filters.
* Aggregate queries (``get_spendings_grouped_by_month`` and
  ``get_most_popular_products``) accept the same explicit filter and
  narrow the result set accordingly.
"""

__all__ = ()

import datetime
from decimal import Decimal

import pytest
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from expenses_counter.services.daos.transaction_dao import TransactionDAO
from expenses_counter.services.database.models.address import Address
from expenses_counter.services.database.models.category import Category
from expenses_counter.services.database.models.product import Product
from expenses_counter.services.database.models.shop import Shop
from expenses_counter.services.database.models.transaction import Transaction
from expenses_counter.services.database.models.user import User


@pytest.fixture
async def two_users_with_transactions(
    db_session: AsyncSession,
) -> dict[str, object]:
    """Seed two users with one transaction each on a rolled-back session.

    Returns:
        dict[str, object]: ``user_a``, ``user_b``, ``tx_a``, ``tx_b``,
            ``product_one``, ``product_two`` to drive per-test assertions.

    """
    user_a = User(
        username="dao-user-a",
        email="dao-user-a@example.com",
        password="hashed-a",
        is_admin=False,
    )
    user_b = User(
        username="dao-user-b",
        email="dao-user-b@example.com",
        password="hashed-b",
        is_admin=False,
    )
    db_session.add_all([user_a, user_b])
    await db_session.flush()

    category = Category(name="DAO-test-category")
    db_session.add(category)
    await db_session.flush()

    shop = Shop(name="DAO-test-shop", category_id=category.id)
    db_session.add(shop)
    await db_session.flush()

    address = Address(local_name="DAO-test-address", address="1 Test Way", shop_id=shop.id)
    product_one = Product(name="DAO-test-product-1", category_id=category.id)
    product_two = Product(name="DAO-test-product-2", category_id=category.id)
    db_session.add_all([address, product_one, product_two])
    await db_session.flush()

    tx_a = Transaction(
        date=datetime.date(2024, 1, 15),
        count=Decimal("1.000"),
        price=Decimal("10.00"),
        product_id=product_one.id,
        address_id=address.id,
        user_id=user_a.id,
    )
    tx_b = Transaction(
        date=datetime.date(2024, 2, 20),
        count=Decimal("2.000"),
        price=Decimal("25.00"),
        product_id=product_two.id,
        address_id=address.id,
        user_id=user_b.id,
    )
    db_session.add_all([tx_a, tx_b])
    await db_session.flush()

    return {
        "user_a": user_a,
        "user_b": user_b,
        "tx_a": tx_a,
        "tx_b": tx_b,
        "product_one": product_one,
        "product_two": product_two,
    }


class TestTransactionDAOFilteredQueries:
    """``TransactionDAO`` honours explicit ``user_id`` filters passed by the route."""

    async def test_get_all_with_user_id_filter_returns_only_owners_rows(
        self,
        db_session: AsyncSession,
        two_users_with_transactions: dict[str, object],
    ) -> None:
        """``get_all(filters=[Transaction.user_id == X])`` returns only X's rows."""
        user_a = two_users_with_transactions["user_a"]
        user_b = two_users_with_transactions["user_b"]
        tx_a = two_users_with_transactions["tx_a"]
        tx_b = two_users_with_transactions["tx_b"]

        dao = TransactionDAO(session=db_session)

        rows_a, total_a = await dao.get_all(filters=[Transaction.user_id == user_a.id])
        rows_b, total_b = await dao.get_all(filters=[Transaction.user_id == user_b.id])

        assert total_a == 1
        assert total_b == 1
        assert [tx.id for tx in rows_a] == [tx_a.id]
        assert [tx.id for tx in rows_b] == [tx_b.id]

    async def test_get_all_without_filters_returns_rows_across_users(
        self,
        db_session: AsyncSession,
        two_users_with_transactions: dict[str, object],
    ) -> None:
        """Without a per-user filter, both seeded rows are visible (admin view)."""
        tx_a = two_users_with_transactions["tx_a"]
        tx_b = two_users_with_transactions["tx_b"]

        dao = TransactionDAO(session=db_session)
        rows, total = await dao.get_all()

        ids = {tx.id for tx in rows}
        assert {tx_a.id, tx_b.id}.issubset(ids)
        assert total >= 2

    async def test_get_by_pk_with_user_id_filter_blocks_other_users_row(
        self,
        db_session: AsyncSession,
        two_users_with_transactions: dict[str, object],
    ) -> None:
        """``get_by_pk`` raises when the filter excludes the row's owner."""
        user_a = two_users_with_transactions["user_a"]
        tx_a = two_users_with_transactions["tx_a"]
        tx_b = two_users_with_transactions["tx_b"]

        dao = TransactionDAO(session=db_session)

        own = await dao.get_by_pk(tx_a.id, filters=[Transaction.user_id == user_a.id])
        assert own.id == tx_a.id
        assert own.user_id == user_a.id

        with pytest.raises(NoResultFound):
            await dao.get_by_pk(tx_b.id, filters=[Transaction.user_id == user_a.id])

    async def test_get_spendings_grouped_by_month_honours_user_id_filter(
        self,
        db_session: AsyncSession,
        two_users_with_transactions: dict[str, object],
    ) -> None:
        """Per-month spending aggregates only rows that pass the filter."""
        user_a = two_users_with_transactions["user_a"]
        user_b = two_users_with_transactions["user_b"]

        dao = TransactionDAO(session=db_session)

        spendings_a = await dao.get_spendings_grouped_by_month(filters=[Transaction.user_id == user_a.id])
        spendings_b = await dao.get_spendings_grouped_by_month(filters=[Transaction.user_id == user_b.id])

        assert spendings_a == [("2024-01-01", Decimal("10.00"))]
        assert spendings_b == [("2024-02-01", Decimal("25.00"))]

    async def test_get_most_popular_products_honours_user_id_filter(
        self,
        db_session: AsyncSession,
        two_users_with_transactions: dict[str, object],
    ) -> None:
        """Popular products only count rows that pass the filter."""
        user_a = two_users_with_transactions["user_a"]
        user_b = two_users_with_transactions["user_b"]
        product_one = two_users_with_transactions["product_one"]
        product_two = two_users_with_transactions["product_two"]

        dao = TransactionDAO(session=db_session)

        popular_a = await dao.get_most_popular_products(filters=[Transaction.user_id == user_a.id])
        popular_b = await dao.get_most_popular_products(filters=[Transaction.user_id == user_b.id])

        assert {p.id for p in popular_a} == {product_one.id}
        assert {p.id for p in popular_b} == {product_two.id}
