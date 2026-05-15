"""API tests for the ``admin_required`` gate on ``/api/v1`` routers.

The address, category, shop, and product routers require ``user_authorized``
at the router level. ``admin_required`` is applied per-endpoint to the write
operations and per-item reads, while list endpoints remain open to any
authenticated user. This module verifies both halves of that contract: a
non-admin user gets 403 on admin-gated routes and 200 on the user-only ones.
"""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import NoResultFound

from expenses_counter.modules.app import get_app
from expenses_counter.modules.middlewares.dependencies import user_authorized
from expenses_counter.modules.middlewares.dependencies.daos import (
    get_address,
    get_category,
    get_product,
    get_shop,
)

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
    ("GET", "/api/v1/category/parent"),
    ("GET", "/api/v1/category/parent/1"),
    ("GET", "/api/v1/shop"),
    ("GET", "/api/v1/product"),
    ("GET", "/api/v1/address"),
]


def _async_dao_mock() -> AsyncMock:
    """Return a generic async DAO mock for routes that resolve a DAO dependency.

    ``get_all`` returns an empty paginated result so list handlers can
    serialize a 200 response without needing a real database row.

    """
    dao = AsyncMock()
    dao.get_all = AsyncMock(return_value=([], 0))
    dao.__aenter__ = AsyncMock(return_value=dao)
    dao.__aexit__ = AsyncMock(return_value=None)
    return dao


@pytest.fixture
def non_admin_client(mock_non_admin_user, test_config):
    """Return a ``TestClient`` authenticated as a non-admin user.

    DAO dependencies are stubbed so request resolution does not require a
    live database; the assertion is purely that ``admin_required`` rejects
    the request before any DAO method is invoked.

    Args:
        mock_non_admin_user: Mock ``User`` with ``is_admin=False``.
        test_config: Test configuration fixture.

    Yields:
        TestClient: Client whose ``user_authorized`` returns a non-admin user.

    """
    app = get_app(test_config)

    app.dependency_overrides[user_authorized] = lambda: mock_non_admin_user
    app.dependency_overrides[get_category] = lambda: _async_dao_mock()
    app.dependency_overrides[get_shop] = lambda: _async_dao_mock()
    app.dependency_overrides[get_product] = lambda: _async_dao_mock()
    app.dependency_overrides[get_address] = lambda: _async_dao_mock()

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

    def test_non_admin_can_look_up_address_by_local_name(self, non_admin_client: TestClient) -> None:
        """Address-by-local-name lookup is user-only; 404 confirms the handler ran."""
        dao = _async_dao_mock()
        # 404 is fine — what matters is we are not blocked by ``admin_required``.
        dao.get_by_address = AsyncMock(side_effect=NoResultFound("Address not found"))
        non_admin_client.app.dependency_overrides[get_address] = lambda: dao

        response = non_admin_client.get("/api/v1/address/name/unknown")
        assert response.status_code == 404


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
        app.dependency_overrides[get_category] = lambda: category_dao

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
