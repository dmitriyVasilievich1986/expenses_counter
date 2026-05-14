"""Integration tests for user API endpoints.

These tests exercise the ``/api/v1/user`` router end-to-end against the real
test database with a real signed JWT for the persistent test user. They
verify that ``GET /user/me`` returns the authenticated identity and that
``PUT`` / ``PATCH`` actually persist changes that subsequent requests can
read back.
"""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from expenses_counter.config import AppConfig
from expenses_counter.modules.app import get_app
from expenses_counter.services.database.models.user import User


@pytest.fixture
def test_app(test_config: AppConfig, test_user_in_db: User):  # noqa: ARG001
    """Application backed by the persistent test user.

    Args:
        test_config: Test configuration with database settings.
        test_user_in_db: Real ``User`` row used as the authenticated principal.

    Yields:
        FastAPI: Application instance for testing.

    """
    app = get_app(test_config)
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
def client(test_app, test_database_with_migrations, auth_headers) -> TestClient:  # noqa: ARG001
    """Build an authenticated ``TestClient`` for the persistent test user.

    Args:
        test_app: The test FastAPI application.
        test_database_with_migrations: Ensure database is set up.
        auth_headers: ``Authorization: Bearer <token>`` for the test user.

    Returns:
        TestClient: Authenticated client.

    """
    return TestClient(test_app, headers=auth_headers)


@pytest.fixture
def restore_user(client: TestClient) -> Iterator[None]:
    """Reset the persistent user's editable fields after each test.

    The session-scoped ``test_user_in_db`` row is shared across tests, so an
    update here would leak into the next test. This fixture snapshots the
    profile before the test and restores it via ``PATCH`` afterwards.

    Args:
        client: Authenticated test client.

    Yields:
        None: Control passes to the test; restoration runs on teardown.

    """
    snapshot = client.get("/api/v1/user/me").json()
    try:
        yield
    finally:
        client.patch(
            "/api/v1/user",
            json={
                "firstName": snapshot.get("firstName"),
                "lastName": snapshot.get("lastName"),
                "photoUrl": snapshot.get("photoUrl"),
            },
        )


@pytest.mark.integration
class TestUserIntegration:
    """End-to-end coverage of the user-profile router."""

    def test_get_me_returns_authenticated_user(self, client: TestClient, test_user_in_db: User):
        """``GET /user/me`` returns the persistent test user's identity."""
        response = client.get("/api/v1/user/me")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user_in_db.id
        assert data["username"] == test_user_in_db.username
        assert data["email"] == test_user_in_db.email
        assert data["isActive"] is True

    def test_put_replaces_user_profile(self, client: TestClient, restore_user):  # noqa: ARG002
        """``PUT /user`` writes the payload and a subsequent GET reflects it."""
        payload = {
            "firstName": "Integration",
            "lastName": "Tester",
            "photoUrl": "https://example.com/integration.png",
        }
        response = client.put("/api/v1/user", json=payload)

        assert response.status_code == 200
        body = response.json()
        assert body["firstName"] == "Integration"
        assert body["lastName"] == "Tester"
        assert body["photoUrl"] == "https://example.com/integration.png"

        # Read-after-write through a fresh request to ensure persistence.
        read = client.get("/api/v1/user/me")
        assert read.status_code == 200
        assert read.json()["firstName"] == "Integration"
        assert read.json()["lastName"] == "Tester"

    def test_put_requires_first_and_last_name(self, client: TestClient):
        """``PUT`` rejects payloads missing required fields with 422."""
        response = client.put("/api/v1/user", json={"firstName": "Only"})
        assert response.status_code == 422

    def test_patch_updates_only_provided_fields(self, client: TestClient, restore_user):  # noqa: ARG002
        """``PATCH`` leaves omitted fields untouched."""
        seed = {
            "firstName": "Before",
            "lastName": "Patch",
            "photoUrl": "https://example.com/seed.png",
        }
        seed_response = client.put("/api/v1/user", json=seed)
        assert seed_response.status_code == 200

        patch_response = client.patch("/api/v1/user", json={"firstName": "After"})
        assert patch_response.status_code == 200
        body = patch_response.json()
        assert body["firstName"] == "After"
        assert body["lastName"] == "Patch"
        assert body["photoUrl"] == "https://example.com/seed.png"

    def test_patch_can_clear_photo_url(self, client: TestClient, restore_user):  # noqa: ARG002
        """An explicit ``null`` for ``photoUrl`` clears the stored value."""
        seed = {
            "firstName": "Pic",
            "lastName": "Owner",
            "photoUrl": "https://example.com/old.png",
        }
        assert client.put("/api/v1/user", json=seed).status_code == 200

        patch_response = client.patch("/api/v1/user", json={"photoUrl": None})
        assert patch_response.status_code == 200
        assert patch_response.json()["photoUrl"] is None

    def test_patch_rejects_empty_first_name(self, client: TestClient):
        """``firstName`` cannot be empty when present in the patch body."""
        response = client.patch("/api/v1/user", json={"firstName": ""})
        assert response.status_code == 422
