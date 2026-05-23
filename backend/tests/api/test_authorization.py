"""API authorization tests.

Every protected router declares ``Depends(user_authorized)``. This module
exercises the gate itself: missing, malformed, or invalid Bearer tokens must
be rejected before the route handler runs. Each protected endpoint is hit
once per scenario via parametrization so that adding a new router
automatically picks up the same coverage by extending ``PROTECTED_ROUTES``.
"""

from unittest.mock import MagicMock

import jwt
import pytest
from fastapi.testclient import TestClient

from expenses_counter.modules.app import get_app
from expenses_counter.modules.middlewares.dependencies import get_db

# (method, path) pairs for routes that require Authorization. Body content is
# irrelevant: the request never reaches the handler when auth fails, so we use
# the cheapest URL per verb. Routes with path params use placeholder ids that
# would otherwise 404 — but auth runs first, so the auth response wins.
PROTECTED_ROUTES: list[tuple[str, str]] = [
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
    ("DELETE", "/api/v1/shop/1"),
    ("GET", "/api/v1/address"),
    ("GET", "/api/v1/address/1"),
    ("POST", "/api/v1/address"),
    ("PUT", "/api/v1/address/1"),
    ("DELETE", "/api/v1/address/1"),
    ("GET", "/api/v1/product"),
    ("GET", "/api/v1/product/1"),
    ("POST", "/api/v1/product"),
    ("PUT", "/api/v1/product/1"),
    ("DELETE", "/api/v1/product/1"),
    ("GET", "/api/v1/transaction"),
    ("GET", "/api/v1/transaction/1"),
    ("POST", "/api/v1/transaction"),
    ("PUT", "/api/v1/transaction/1"),
    ("DELETE", "/api/v1/transaction/1"),
    ("GET", "/api/v1/user/me"),
    ("PUT", "/api/v1/user"),
    ("PATCH", "/api/v1/user"),
]


@pytest.fixture
def unauthorized_client(test_config):
    """Return a ``TestClient`` with ``user_authorized`` left intact.

    ``get_db`` is overridden with a ``MagicMock`` so the real database client
    is not contacted — auth failures must short-circuit before the handler
    receives a DAO anyway, but the JWT decode path runs after ``get_db`` is
    resolved.

    Args:
        test_config: Test configuration fixture.

    Yields:
        TestClient: Client that does NOT pre-authenticate requests.

    """
    app = get_app(test_config)
    app.dependency_overrides[get_db] = lambda: MagicMock()
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.mark.api
class TestMissingAuthorizationHeader:
    """Requests with no ``Authorization`` header must be rejected."""

    @pytest.mark.parametrize(("method", "path"), PROTECTED_ROUTES)
    def test_protected_route_rejects_missing_header(
        self, unauthorized_client: TestClient, method: str, path: str
    ) -> None:
        """``user_authorized`` aborts unauthenticated requests with 401."""
        response = unauthorized_client.request(method, path)
        assert response.status_code == 401
        assert response.json()["detail"] == "Unauthorized"


@pytest.mark.api
class TestInvalidAuthorizationHeader:
    """Bearer tokens that are present but unusable must produce 401."""

    @pytest.mark.parametrize(("method", "path"), PROTECTED_ROUTES)
    def test_protected_route_rejects_malformed_jwt(
        self, unauthorized_client: TestClient, method: str, path: str
    ) -> None:
        """A non-JWT bearer value must fail decoding and return 401."""
        response = unauthorized_client.request(method, path, headers={"Authorization": "Bearer not-a-real-jwt"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid token"

    @pytest.mark.parametrize(("method", "path"), PROTECTED_ROUTES)
    def test_protected_route_rejects_wrong_secret(
        self, unauthorized_client: TestClient, method: str, path: str
    ) -> None:
        """A JWT signed with the wrong key must fail signature verification."""
        forged = jwt.encode({"user_id": 1}, "wrong-secret", algorithm="HS256")
        response = unauthorized_client.request(method, path, headers={"Authorization": f"Bearer {forged}"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid token"

    def test_protected_route_rejects_non_bearer_scheme(self, unauthorized_client: TestClient) -> None:
        """Schemes other than ``Bearer`` collapse to a missing token and return 401."""
        response = unauthorized_client.get("/api/v1/category", headers={"Authorization": "Basic dXNlcjpwYXNz"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Unauthorized"

    def test_protected_route_rejects_expired_token(self, unauthorized_client: TestClient) -> None:
        """Expired JWTs surface the dedicated ``Token expired`` 401 detail."""
        # iat/exp far in the past — relies on the same secret the app verifies with.
        expired = jwt.encode({"user_id": 1, "exp": 0}, "test-jwt-secret-key-only-for-tests", algorithm="HS256")
        response = unauthorized_client.get("/api/v1/category", headers={"Authorization": f"Bearer {expired}"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Token expired"
