"""Integration tests for the protected-route authorization flow.

These tests exercise ``user_authorized`` end-to-end against the real database
and JWT service: a valid Bearer token (signed with the test secret for a user
that exists in the database) must succeed, while missing, malformed, or
mismatched tokens must be rejected by the dependency.
"""

import jwt
import pytest
from fastapi.testclient import TestClient

from expenses_counter.config import AppConfig
from expenses_counter.modules.app import get_app
from expenses_counter.services.auth import JWTTokenService
from expenses_counter.services.database.models.user import User
from tests.conftest import TEST_JWT_SECRET


@pytest.fixture
def test_app(test_config: AppConfig, test_user_in_db: User):  # noqa: ARG001
    """Application configured to run the real auth pipeline.

    ``test_user_in_db`` ensures the user referenced by issued tokens exists,
    so JWT verification can be followed by a successful DB lookup.

    Args:
        test_config: Test configuration with database settings.
        test_user_in_db: Persisted user wired to the issued tokens.

    Returns:
        FastAPI: Application instance with no dependency overrides.

    """
    app = get_app(test_config)
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
def client(test_app, test_database_with_migrations) -> TestClient:  # noqa: ARG001
    """Bare ``TestClient`` — no default ``Authorization`` header.

    Args:
        test_app: Application fixture.
        test_database_with_migrations: Ensure database is set up.

    Returns:
        TestClient: Client that sends no auth header by default.

    """
    return TestClient(test_app)


@pytest.mark.integration
class TestAuthorizationEndToEnd:
    """End-to-end verification of the Bearer-token gate on a real router."""

    def test_valid_token_grants_access(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """A token signed for an existing user must reach the handler."""
        response = client.get("/api/v1/category", headers=auth_headers)
        assert response.status_code == 200

    def test_missing_header_is_rejected(self, client: TestClient) -> None:
        """Requests without ``Authorization`` must be rejected by ``HTTPBearer``."""
        response = client.get("/api/v1/category")
        assert response.status_code == 403
        assert response.json()["detail"] == "Not authenticated"

    def test_malformed_token_is_rejected(self, client: TestClient) -> None:
        """A bearer value that is not a JWT must fail decoding."""
        response = client.get("/api/v1/category", headers={"Authorization": "Bearer this-is-not-a-jwt"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid token"

    def test_token_signed_with_wrong_secret_is_rejected(self, client: TestClient) -> None:
        """A JWT signed under a different secret must fail signature verification."""
        forged = jwt.encode({"user_id": 1}, "wrong-secret", algorithm="HS256")
        response = client.get("/api/v1/category", headers={"Authorization": f"Bearer {forged}"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid token"

    def test_expired_token_is_rejected(self, client: TestClient) -> None:
        """An expired JWT must surface as ``Token expired``."""
        expired = jwt.encode({"user_id": 1, "exp": 0}, TEST_JWT_SECRET, algorithm="HS256")
        response = client.get("/api/v1/category", headers={"Authorization": f"Bearer {expired}"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Token expired"

    def test_token_for_unknown_user_is_rejected(self, client: TestClient) -> None:
        """A correctly signed JWT for a missing user must return 401."""
        token = JWTTokenService(TEST_JWT_SECRET).generate_token(999_999).token
        response = client.get("/api/v1/category", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 401
        assert response.json()["detail"] == "User not found"
