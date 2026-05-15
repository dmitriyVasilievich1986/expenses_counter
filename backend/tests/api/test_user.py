"""API tests for user endpoints.

This module tests the ``/api/v1/user`` router without touching the database.
It mocks ``UserDAO`` and ``user_authorized`` so each test exercises only the
router's behaviour: serialization of the authenticated user, payload
forwarding, and the three failure branches (``NoResultFound`` -> 404,
``IntegrityError`` -> 400, ``SQLAlchemyError`` -> 500).
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import DatabaseError, IntegrityError, NoResultFound

from expenses_counter.modules.app import get_app
from expenses_counter.modules.middlewares.dependencies import user_authorized
from expenses_counter.modules.middlewares.dependencies.daos.user_dao import get_user_dao
from expenses_counter.services.database.models.user import User


@pytest.fixture
def mock_user_dao():
    """Create a mock ``UserDAO`` for testing.

    Returns:
        AsyncMock: Mocked ``UserDAO`` instance.

    """
    dao = AsyncMock()
    dao.update = AsyncMock()

    dao.__aenter__ = AsyncMock(return_value=dao)
    dao.__aexit__ = AsyncMock(return_value=None)

    return dao


@pytest.fixture
def authenticated_user() -> MagicMock:
    """Return a fully-populated mock ``User`` for ``user_authorized``.

    Unlike the session-scoped ``mock_user`` fixture, this one carries every
    field that ``GetSingleUserResponse`` serializes so route handlers that
    echo the authenticated user back to the client (``GET /user/me``) don't
    receive ``MagicMock`` sentinels in unrelated attributes.

    Returns:
        MagicMock: A mock user with stable values for every response field.

    """
    user = MagicMock(spec=User)
    user.id = 1
    user.username = "testuser"
    user.email = "test@example.com"
    user.first_name = "Test"
    user.last_name = "User"
    user.photo_url = "https://example.com/photo.png"
    user.is_active = True
    return user


@pytest.fixture
def test_client(mock_user_dao, authenticated_user, test_config):
    """Create a test client with mocked dependencies.

    Args:
        mock_user_dao: Mocked ``UserDAO`` instance.
        authenticated_user: Mocked authenticated user.
        test_config: Test configuration fixture.

    Returns:
        TestClient: FastAPI test client with overridden dependencies.

    """
    app = get_app(test_config)

    app.dependency_overrides[get_user_dao] = lambda: mock_user_dao
    app.dependency_overrides[user_authorized] = lambda: authenticated_user

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()


def _make_updated_user(
    *,
    user_id: int = 1,
    first_name: str = "Updated",
    last_name: str = "Person",
    photo_url: str | None = "https://example.com/new.png",
    username: str = "testuser",
    email: str = "test@example.com",
    is_active: bool = True,
) -> MagicMock:
    """Build a mock ``User`` that ``GetSingleUserResponse`` can serialize.

    Args:
        user_id: Primary key for the user.
        first_name: First name to return.
        last_name: Last name to return.
        photo_url: Photo URL or ``None``.
        username: Username to echo back.
        email: Email to echo back.
        is_active: Whether the user is active.

    Returns:
        MagicMock: User-like mock with all fields populated.

    """
    user = MagicMock(spec=User)
    user.id = user_id
    user.username = username
    user.email = email
    user.first_name = first_name
    user.last_name = last_name
    user.photo_url = photo_url
    user.is_active = is_active
    return user


@pytest.mark.api
class TestGetMe:
    """Test GET /api/v1/user/me endpoint."""

    def test_get_me_returns_authenticated_user(self, test_client, authenticated_user):
        """The authenticated user is echoed back as the response body."""
        response = test_client.get("/api/v1/user/me")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == authenticated_user.id
        assert data["username"] == authenticated_user.username
        assert data["email"] == authenticated_user.email
        assert data["firstName"] == authenticated_user.first_name
        assert data["lastName"] == authenticated_user.last_name
        assert data["photoUrl"] == authenticated_user.photo_url
        assert data["isActive"] == authenticated_user.is_active

    def test_get_me_does_not_hit_user_dao(self, test_client, mock_user_dao):
        """``/me`` only inspects the user injected by ``user_authorized``."""
        response = test_client.get("/api/v1/user/me")

        assert response.status_code == 200
        mock_user_dao.update.assert_not_called()


@pytest.mark.api
class TestPutMe:
    """Test PUT /api/v1/user endpoint."""

    def test_put_me_success(self, test_client, mock_user_dao, authenticated_user):
        """A full payload is forwarded to ``UserDAO.update`` and serialized."""
        updated = _make_updated_user(
            user_id=authenticated_user.id,
            first_name="NewFirst",
            last_name="NewLast",
            photo_url="https://example.com/new.png",
        )
        mock_user_dao.update.return_value = updated

        payload = {
            "firstName": "NewFirst",
            "lastName": "NewLast",
            "photoUrl": "https://example.com/new.png",
        }
        response = test_client.put("/api/v1/user", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["firstName"] == "NewFirst"
        assert data["lastName"] == "NewLast"
        assert data["photoUrl"] == "https://example.com/new.png"
        mock_user_dao.update.assert_called_once_with(
            authenticated_user.id,
            first_name="NewFirst",
            last_name="NewLast",
            photo_url="https://example.com/new.png",
        )

    def test_put_me_forwards_null_photo_url(self, test_client, mock_user_dao, authenticated_user):
        """``PutUserBody`` permits a null ``photoUrl`` and forwards it."""
        updated = _make_updated_user(
            user_id=authenticated_user.id,
            first_name="NewFirst",
            last_name="NewLast",
            photo_url=None,
        )
        mock_user_dao.update.return_value = updated

        payload = {"firstName": "NewFirst", "lastName": "NewLast", "photoUrl": None}
        response = test_client.put("/api/v1/user", json=payload)

        assert response.status_code == 200
        assert response.json()["photoUrl"] is None
        mock_user_dao.update.assert_called_once_with(
            authenticated_user.id,
            first_name="NewFirst",
            last_name="NewLast",
            photo_url=None,
        )

    def test_put_me_not_found(self, test_client, mock_user_dao):
        """``NoResultFound`` surfaces as a 404."""
        mock_user_dao.update.side_effect = NoResultFound("User not found")

        payload = {"firstName": "NewFirst", "lastName": "NewLast"}
        response = test_client.put("/api/v1/user", json=payload)

        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"

    def test_put_me_integrity_error(self, test_client, mock_user_dao):
        """``IntegrityError`` surfaces as a 400 with the documented detail."""
        mock_user_dao.update.side_effect = IntegrityError(
            "UPDATE main_user", None, Exception("unique constraint failed")
        )

        payload = {"firstName": "NewFirst", "lastName": "NewLast"}
        response = test_client.put("/api/v1/user", json=payload)

        assert response.status_code == 400
        assert response.json()["detail"] == "Related object not found"

    def test_put_me_db_error(self, test_client, mock_user_dao):
        """Any other SQLAlchemy error surfaces as a 500."""
        mock_user_dao.update.side_effect = DatabaseError("UPDATE main_user", None, Exception("connection lost"))

        payload = {"firstName": "NewFirst", "lastName": "NewLast"}
        response = test_client.put("/api/v1/user", json=payload)

        assert response.status_code == 500
        assert "updating" in response.json()["detail"].lower()

    def test_put_me_missing_required_field(self, test_client):
        """``PutUserBody`` requires both ``firstName`` and ``lastName``."""
        response = test_client.put("/api/v1/user", json={"firstName": "Only"})

        assert response.status_code == 422

    def test_put_me_rejects_empty_first_name(self, test_client):
        """``firstName`` must be at least one character long."""
        payload = {"firstName": "", "lastName": "Last"}
        response = test_client.put("/api/v1/user", json=payload)

        assert response.status_code == 422

    def test_put_me_rejects_first_name_over_max_length(self, test_client):
        """``firstName`` must be at most 150 characters."""
        payload = {"firstName": "x" * 151, "lastName": "Last"}
        response = test_client.put("/api/v1/user", json=payload)

        assert response.status_code == 422


@pytest.mark.api
class TestPatchMe:
    """Test PATCH /api/v1/user endpoint."""

    def test_patch_me_partial_update(self, test_client, mock_user_dao, authenticated_user):
        """Only fields present in the body are forwarded to ``update``."""
        updated = _make_updated_user(
            user_id=authenticated_user.id,
            first_name="PatchedFirst",
            last_name=authenticated_user.last_name,
            photo_url=authenticated_user.photo_url,
        )
        mock_user_dao.update.return_value = updated

        response = test_client.patch("/api/v1/user", json={"firstName": "PatchedFirst"})

        assert response.status_code == 200
        assert response.json()["firstName"] == "PatchedFirst"
        mock_user_dao.update.assert_called_once_with(
            authenticated_user.id,
            first_name="PatchedFirst",
        )

    def test_patch_me_empty_body_forwards_no_fields(self, test_client, mock_user_dao, authenticated_user):
        """``exclude_unset=True`` means an empty body forwards no kwargs."""
        mock_user_dao.update.return_value = _make_updated_user(
            user_id=authenticated_user.id,
            first_name=authenticated_user.first_name,
            last_name=authenticated_user.last_name,
            photo_url=authenticated_user.photo_url,
        )

        response = test_client.patch("/api/v1/user", json={})

        assert response.status_code == 200
        mock_user_dao.update.assert_called_once_with(authenticated_user.id)

    def test_patch_me_forwards_explicit_null_photo_url(self, test_client, mock_user_dao, authenticated_user):
        """An explicit ``photoUrl: null`` is forwarded (clears the field)."""
        mock_user_dao.update.return_value = _make_updated_user(
            user_id=authenticated_user.id,
            first_name=authenticated_user.first_name,
            last_name=authenticated_user.last_name,
            photo_url=None,
        )

        response = test_client.patch("/api/v1/user", json={"photoUrl": None})

        assert response.status_code == 200
        assert response.json()["photoUrl"] is None
        mock_user_dao.update.assert_called_once_with(authenticated_user.id, photo_url=None)

    def test_patch_me_not_found(self, test_client, mock_user_dao):
        """``NoResultFound`` surfaces as a 404."""
        mock_user_dao.update.side_effect = NoResultFound("User not found")

        response = test_client.patch("/api/v1/user", json={"firstName": "X"})

        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"

    def test_patch_me_integrity_error(self, test_client, mock_user_dao):
        """``IntegrityError`` surfaces as a 400."""
        mock_user_dao.update.side_effect = IntegrityError(
            "UPDATE main_user", None, Exception("unique constraint failed")
        )

        response = test_client.patch("/api/v1/user", json={"firstName": "X"})

        assert response.status_code == 400
        assert response.json()["detail"] == "Related object not found"

    def test_patch_me_db_error(self, test_client, mock_user_dao):
        """Any other SQLAlchemy error surfaces as a 500."""
        mock_user_dao.update.side_effect = DatabaseError("UPDATE main_user", None, Exception("connection lost"))

        response = test_client.patch("/api/v1/user", json={"firstName": "X"})

        assert response.status_code == 500
        assert "patching" in response.json()["detail"].lower()

    def test_patch_me_rejects_empty_first_name(self, test_client):
        """``firstName`` cannot be the empty string when present."""
        response = test_client.patch("/api/v1/user", json={"firstName": ""})

        assert response.status_code == 422

    def test_patch_me_rejects_first_name_over_max_length(self, test_client):
        """``firstName`` is bounded to 150 characters when present."""
        response = test_client.patch("/api/v1/user", json={"firstName": "x" * 151})

        assert response.status_code == 422


@pytest.mark.api
class TestGetAvailablePages:
    """Test GET /api/v1/user/available-pages endpoint."""

    def _build_client(self, test_config, mock_user_dao, user: MagicMock) -> TestClient:
        """Wire a ``TestClient`` whose ``user_authorized`` resolves to ``user``."""
        app = get_app(test_config)
        app.dependency_overrides[get_user_dao] = lambda: mock_user_dao
        app.dependency_overrides[user_authorized] = lambda: user
        return TestClient(app)

    def test_admin_user_sees_admin_pages(self, test_config, mock_user_dao):
        """Admin users get the admin-only page keys."""
        admin = MagicMock(spec=User)
        admin.is_admin = True
        client = self._build_client(test_config, mock_user_dao, admin)

        try:
            response = client.get("/api/v1/user/available-pages")
        finally:
            client.app.dependency_overrides.clear()

        assert response.status_code == 200
        assert response.json() == ["shops", "products"]

    def test_non_admin_user_sees_empty_list(self, test_config, mock_user_dao):
        """Non-admin users get no admin-gated page keys."""
        regular = MagicMock(spec=User)
        regular.is_admin = False
        client = self._build_client(test_config, mock_user_dao, regular)

        try:
            response = client.get("/api/v1/user/available-pages")
        finally:
            client.app.dependency_overrides.clear()

        assert response.status_code == 200
        assert response.json() == []

    def test_response_differs_between_admin_and_non_admin(self, test_config, mock_user_dao):
        """The same endpoint must return different payloads for the two roles."""
        admin = MagicMock(spec=User)
        admin.is_admin = True
        regular = MagicMock(spec=User)
        regular.is_admin = False

        admin_client = self._build_client(test_config, mock_user_dao, admin)
        try:
            admin_pages = admin_client.get("/api/v1/user/available-pages").json()
        finally:
            admin_client.app.dependency_overrides.clear()

        regular_client = self._build_client(test_config, mock_user_dao, regular)
        try:
            regular_pages = regular_client.get("/api/v1/user/available-pages").json()
        finally:
            regular_client.app.dependency_overrides.clear()

        assert admin_pages != regular_pages
        assert set(admin_pages) - set(regular_pages) == {"shops", "products"}
