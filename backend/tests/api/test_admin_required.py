"""API tests for the ``admin_required`` gate on ``/api/v1`` routers.

The category, product, and shop routers are admin-only end-to-end. The address
router applies ``admin_required`` to every endpoint except the two list/lookup
reads (``GET /address`` and ``GET /address/name/{local_name}``). This module
exercises a request per admin-protected ``(method, path)`` pair with an
authenticated non-admin user and asserts the dependency rejects it with 403.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

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
    ("GET", "/api/v1/category"),
    ("GET", "/api/v1/category/1"),
    ("GET", "/api/v1/category/parent"),
    ("GET", "/api/v1/category/parent/1"),
    ("POST", "/api/v1/category"),
    ("PUT", "/api/v1/category/1"),
    ("PATCH", "/api/v1/category/1"),
    ("DELETE", "/api/v1/category/1"),
    ("GET", "/api/v1/shop"),
    ("GET", "/api/v1/shop/1"),
    ("POST", "/api/v1/shop"),
    ("PUT", "/api/v1/shop/1"),
    ("PATCH", "/api/v1/shop/1"),
    ("DELETE", "/api/v1/shop/1"),
    ("GET", "/api/v1/product"),
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


def _async_dao_mock() -> AsyncMock:
    """Return a generic async DAO mock for routes that resolve a DAO dependency."""
    dao = AsyncMock()
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
        category_dao.get_all = AsyncMock(return_value=([], 0))

        app.dependency_overrides[user_authorized] = lambda: mock_user
        app.dependency_overrides[get_category] = lambda: category_dao

        client = TestClient(app)
        yield client

        app.dependency_overrides.clear()

    def test_admin_passes_admin_required_gate(self, admin_client: TestClient) -> None:
        """An admin reaches the handler — the gate must not short-circuit with 403."""
        response = admin_client.get("/api/v1/category")
        assert response.status_code == 200


@pytest.mark.api
class TestAddressPublicReadsAllowedForNonAdmin:
    """``GET /address`` and ``GET /address/name/{local_name}`` skip the admin gate."""

    def test_non_admin_can_list_addresses(self, non_admin_client: TestClient) -> None:
        """Listing addresses must remain available to authenticated non-admin users."""
        # The injected address DAO is a bare AsyncMock; override its get_all to
        # return an empty page so the handler can serialize a valid response.
        from expenses_counter.modules.middlewares.dependencies.daos import get_address as _get_address

        dao = _async_dao_mock()
        dao.get_all = AsyncMock(return_value=([], 0))
        non_admin_client.app.dependency_overrides[_get_address] = lambda: dao

        response = non_admin_client.get("/api/v1/address")
        assert response.status_code == 200

    def test_non_admin_can_look_up_address_by_local_name(self, non_admin_client: TestClient) -> None:
        """Resolving an address by local name must not require admin privileges."""
        from sqlalchemy.exc import NoResultFound

        from expenses_counter.modules.middlewares.dependencies.daos import get_address as _get_address

        dao = _async_dao_mock()
        # 404 is fine — what matters is we are not blocked by ``admin_required``.
        dao.get_by_address = AsyncMock(side_effect=NoResultFound("Address not found"))
        non_admin_client.app.dependency_overrides[_get_address] = lambda: dao

        response = non_admin_client.get("/api/v1/address/name/unknown")
        assert response.status_code == 404
