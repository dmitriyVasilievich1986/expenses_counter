"""Unit tests for ``TransactionDAO`` user-scoped filtering.

These tests exercise the DAO directly against a real (SQLite) database via the
``db_session`` fixture and verify that:

* Non-admin users only see their own transactions.
* Admin users see every transaction regardless of ``user_id``.
* Aggregated queries (``get_spendings_grouped_by_month`` and
  ``get_most_popular_products``) honour the same per-user filter.
* The constructor refuses to build a DAO without a ``user``.
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
    """Seed two non-admin users, an admin, and one transaction per non-admin user.

    All rows are inserted on ``db_session`` so the surrounding transaction is
    rolled back at the end of the test, keeping isolation guarantees from the
    shared ``db_session`` fixture.

    Returns:
        dict[str, object]: The two regular users, the admin, and the two
            transactions keyed as ``user_a``, ``user_b``, ``admin``, ``tx_a``,
            ``tx_b``.

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
    admin = User(
        username="dao-admin",
        email="dao-admin@example.com",
        password="hashed-admin",
        is_admin=True,
    )
    db_session.add_all([user_a, user_b, admin])
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
        "admin": admin,
        "tx_a": tx_a,
        "tx_b": tx_b,
        "product_one": product_one,
        "product_two": product_two,
    }


class TestTransactionDAOConstructor:
    """Direct ``TransactionDAO.__init__`` validation."""

    async def test_missing_user_raises(self, db_session: AsyncSession) -> None:
        """Constructing without ``user`` must raise ``ValueError``."""
        with pytest.raises(ValueError, match="user is required"):
            TransactionDAO(session=db_session)

    async def test_non_admin_user_sets_base_filters(self, db_session: AsyncSession) -> None:
        """A non-admin user populates ``base_filters`` with a ``user_id`` predicate."""
        user = User(id=42, username="x", email="x@example.com", password="x", is_admin=False)
        dao = TransactionDAO(session=db_session, user=user)

        assert dao.base_filters is not None
        assert len(dao.base_filters) == 1

    async def test_admin_user_leaves_base_filters_unset(self, db_session: AsyncSession) -> None:
        """An admin user does not install per-user ``base_filters``."""
        admin = User(id=1, username="a", email="a@example.com", password="x", is_admin=True)
        dao = TransactionDAO(session=db_session, user=admin)

        assert getattr(dao, "base_filters", None) is None


class TestTransactionDAOUserScopedQueries:
    """Each non-admin user sees only their own transactions."""

    async def test_get_all_returns_only_owners_transactions(
        self,
        db_session: AsyncSession,
        two_users_with_transactions: dict[str, object],
    ) -> None:
        """``get_all`` must filter by ``user_id`` for non-admin users."""
        user_a = two_users_with_transactions["user_a"]
        user_b = two_users_with_transactions["user_b"]
        tx_a = two_users_with_transactions["tx_a"]
        tx_b = two_users_with_transactions["tx_b"]

        dao_a = TransactionDAO(session=db_session, user=user_a)
        dao_b = TransactionDAO(session=db_session, user=user_b)

        rows_a, total_a = await dao_a.get_all()
        rows_b, total_b = await dao_b.get_all()

        assert total_a == 1
        assert total_b == 1
        assert [tx.id for tx in rows_a] == [tx_a.id]
        assert [tx.id for tx in rows_b] == [tx_b.id]
        assert {tx.user_id for tx in rows_a} == {user_a.id}
        assert {tx.user_id for tx in rows_b} == {user_b.id}

    async def test_get_by_pk_blocks_other_users_transaction(
        self,
        db_session: AsyncSession,
        two_users_with_transactions: dict[str, object],
    ) -> None:
        """``get_by_pk`` must raise when reaching for another user's row."""
        user_a = two_users_with_transactions["user_a"]
        tx_a = two_users_with_transactions["tx_a"]
        tx_b = two_users_with_transactions["tx_b"]

        dao_a = TransactionDAO(session=db_session, user=user_a)

        own = await dao_a.get_by_pk(tx_a.id)
        assert own.id == tx_a.id
        assert own.user_id == user_a.id

        with pytest.raises(NoResultFound):
            await dao_a.get_by_pk(tx_b.id)

    async def test_admin_sees_all_transactions(
        self,
        db_session: AsyncSession,
        two_users_with_transactions: dict[str, object],
    ) -> None:
        """An admin DAO returns transactions across every user."""
        admin = two_users_with_transactions["admin"]
        tx_a = two_users_with_transactions["tx_a"]
        tx_b = two_users_with_transactions["tx_b"]

        dao_admin = TransactionDAO(session=db_session, user=admin)
        rows, total = await dao_admin.get_all()

        ids = {tx.id for tx in rows}
        assert {tx_a.id, tx_b.id}.issubset(ids)
        assert total >= 2

    async def test_get_spendings_grouped_by_month_is_user_scoped(
        self,
        db_session: AsyncSession,
        two_users_with_transactions: dict[str, object],
    ) -> None:
        """Per-month spending aggregates only the caller's own transactions."""
        user_a = two_users_with_transactions["user_a"]
        user_b = two_users_with_transactions["user_b"]

        dao_a = TransactionDAO(session=db_session, user=user_a)
        dao_b = TransactionDAO(session=db_session, user=user_b)

        spendings_a = await dao_a.get_spendings_grouped_by_month()
        spendings_b = await dao_b.get_spendings_grouped_by_month()

        assert spendings_a == [("2024-01-01", 10.0)]
        assert spendings_b == [("2024-02-01", 25.0)]

    async def test_get_most_popular_products_is_user_scoped(
        self,
        db_session: AsyncSession,
        two_users_with_transactions: dict[str, object],
    ) -> None:
        """Popular products only count the calling user's transactions."""
        user_a = two_users_with_transactions["user_a"]
        user_b = two_users_with_transactions["user_b"]
        product_one = two_users_with_transactions["product_one"]
        product_two = two_users_with_transactions["product_two"]

        dao_a = TransactionDAO(session=db_session, user=user_a)
        dao_b = TransactionDAO(session=db_session, user=user_b)

        popular_a = await dao_a.get_most_popular_products()
        popular_b = await dao_b.get_most_popular_products()

        assert {p.id for p in popular_a} == {product_one.id}
        assert {p.id for p in popular_b} == {product_two.id}
