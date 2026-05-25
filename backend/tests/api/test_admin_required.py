"""API tests for the ``admin_required`` gate on ``/api/v1`` routers.

The address, category, shop, and product routers split their endpoints into
two sub-routers: ``all_users`` (requires only ``user_authorized``) and
``admin_only`` (additionally requires ``admin_required``). This module
verifies both halves of that contract: a non-admin user gets 403 on
admin-gated routes and 200 on the user-only ones.
"""

from contextlib import ExitStack
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import NoResultFound

from expenses_counter.modules.app import get_app
from expenses_counter.modules.middlewares.dependencies import get_db, user_authorized

# (method, path) pairs guarded by ``admin_required``. Bodies are intentionally
# minimal — the gate fires before request validation, so a 403 must come back
# regardless of payload shape.
ADMIN_PROTECTED_ROUTES: list[tuple[str, str]] = [
    ("GET", "/api/v1/category/1"),
    ("POST", "/api/v1/category"),
    ("PUT", "/api/v1/category/1"),
    ("PATCH", "/api/v1/category/1"),
    ("DELETE", "/api/v1/category/1"),
    ("GET", "/api/v1/shop/1"),
    ("POST", "/api/v1/shop"),
    ("PUT", "/api/v1/shop/1"),
    ("PATCH", "/api/v1/shop/1"),
    ("DELETE", "/api/v1/shop/1"),
    ("GET", "/api/v1/product/1"),
    ("POST", "/api/v1/product"),
    ("PUT", "/api/v1/product/1"),
    ("PATCH", "/api/v1/product/1"),
    ("DELETE", "/api/v1/product/1"),
    ("GET", "/api/v1/address/1"),
    ("POST", "/api/v1/address"),
    ("PUT", "/api/v1/address/1"),
    ("PATCH", "/api/v1/address/1"),
    ("DELETE", "/api/v1/address/1"),
]

# (method, path) pairs that only require ``user_authorized`` — a non-admin
# user must reach the handler. The DAO mocks resolve list calls to an empty
# page so handlers serialize a valid response.
USER_ONLY_ROUTES: list[tuple[str, str]] = [
    ("GET", "/api/v1/category"),
    ("GET", "/api/v1/shop"),
    ("GET", "/api/v1/product"),
    ("GET", "/api/v1/address"),
]

# Each entity's DAO is imported by both router halves; we patch every import
# site so the same mock backs every endpoint.
_DAO_PATHS = {
    "address": (
        "expenses_counter.modules.routers.api.v1.address.all_users.AddressDAO",
        "expenses_counter.modules.routers.api.v1.address.admin_only.AddressDAO",
    ),
    "category": (
        "expenses_counter.modules.routers.api.v1.category.all_users.CategoryDAO",
        "expenses_counter.modules.routers.api.v1.category.admin_only.CategoryDAO",
    ),
    "product": (
        "expenses_counter.modules.routers.api.v1.product.all_users.ProductDAO",
        "expenses_counter.modules.routers.api.v1.product.admin_only.ProductDAO",
    ),
    "shop": (
        "expenses_counter.modules.routers.api.v1.shop.all_users.ShopDAO",
        "expenses_counter.modules.routers.api.v1.shop.admin_only.ShopDAO",
    ),
}


def _async_dao_mock() -> AsyncMock:
    """Return a generic async DAO mock for routes that resolve a DAO dependency.

    ``get_all`` returns an empty paginated result so list handlers can
    serialize a 200 response without needing a real database row.

    """
    dao = AsyncMock()
    dao.get_all = AsyncMock(return_value=([], 0))
    return dao


@pytest.fixture
def daos() -> dict[str, AsyncMock]:
    """Per-entity mock DAOs reused across patch sites and test bodies."""
    return {name: _async_dao_mock() for name in _DAO_PATHS}


@pytest.fixture
def non_admin_client(mock_non_admin_user, test_config, daos):
    """Return a ``TestClient`` authenticated as a non-admin user.

    DAO class references are patched in every router module so request
    resolution does not require a live database; the assertion is purely
    that ``admin_required`` rejects the request before any DAO method is
    invoked.

    Args:
        mock_non_admin_user: Mock ``User`` with ``is_admin=False``.
        test_config: Test configuration fixture.
        daos: Mapping of entity name to its mock DAO.

    Yields:
        TestClient: Client whose ``user_authorized`` returns a non-admin user.

    """
    app = get_app(test_config)

    app.dependency_overrides[user_authorized] = lambda: mock_non_admin_user
    app.dependency_overrides[get_db] = lambda: MagicMock()

    with ExitStack() as stack:
        for name, paths in _DAO_PATHS.items():
            for path in paths:
                stack.enter_context(patch(path, return_value=daos[name]))
        client = TestClient(app)
        yield client

    app.dependency_overrides.clear()


@pytest.mark.api
class TestAdminRequiredRejectsNonAdmin:
    """Non-admin users must be rejected from admin-only endpoints with 403."""

    @pytest.mark.parametrize(("method", "path"), ADMIN_PROTECTED_ROUTES)
    def test_non_admin_is_forbidden(self, non_admin_client: TestClient, method: str, path: str) -> None:
        """Authenticated but non-admin requests must surface ``admin_required``'s 403."""
        response = non_admin_client.request(method, path, json={})
        assert response.status_code == 403
        assert response.json()["detail"] == "You are not authorized to access this resource"


@pytest.mark.api
class TestUserOnlyRoutesAllowNonAdmin:
    """Non-admin users must be allowed through routes without ``admin_required``."""

    @pytest.mark.parametrize(("method", "path"), USER_ONLY_ROUTES)
    def test_non_admin_reaches_handler(self, non_admin_client: TestClient, method: str, path: str) -> None:
        """The gate skips these routes — handler must return 200 for an authenticated user."""
        response = non_admin_client.request(method, path)
        assert response.status_code == 200


@pytest.mark.api
class TestAdminRequiredAllowsAdmin:
    """Admin users must pass the gate (handler-level outcome is not asserted)."""

    @pytest.fixture
    def admin_client(self, mock_user, test_config):
        """Return a ``TestClient`` authenticated as an admin user.

        Args:
            mock_user: Mock ``User`` with ``is_admin=True`` from conftest.
            test_config: Test configuration fixture.

        Yields:
            TestClient: Client whose ``user_authorized`` returns an admin user.

        """
        app = get_app(test_config)

        category_dao = _async_dao_mock()
        category_dao.get_by_pk = AsyncMock(side_effect=NoResultFound("Category not found"))

        app.dependency_overrides[user_authorized] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: MagicMock()

        with ExitStack() as stack:
            for path in _DAO_PATHS["category"]:
                stack.enter_context(patch(path, return_value=category_dao))
            client = TestClient(app)
            yield client

        app.dependency_overrides.clear()

    def test_admin_passes_admin_required_gate(self, admin_client: TestClient) -> None:
        """An admin reaches an admin-only handler — the gate must not short-circuit with 403.

        ``GET /category/{id}`` is admin-gated; we route it through to a 404 from the DAO
        to prove the request passed ``admin_required`` rather than being blocked at the gate.
        """
        response = admin_client.get("/api/v1/category/1")
        assert response.status_code == 404
