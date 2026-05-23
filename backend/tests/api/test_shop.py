"""API tests for shop endpoints.

This module tests all shop API endpoints without making direct database calls.
It uses FastAPI's TestClient and mocks the ShopDAO dependency.
"""

from contextlib import ExitStack
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import DatabaseError, IntegrityError, NoResultFound

from expenses_counter.modules.app import get_app
from expenses_counter.modules.middlewares.dependencies import get_db, user_authorized

_SHOP_DAO_PATHS = (
    "expenses_counter.modules.routers.api.v1.shop.all_users.ShopDAO",
    "expenses_counter.modules.routers.api.v1.shop.admin_only.ShopDAO",
)


@pytest.fixture
def mock_shop_dao():
    """Create a mock ShopDAO for testing.

    Returns:
        AsyncMock: Mocked ShopDAO instance.

    """
    dao = AsyncMock()
    dao.get_all = AsyncMock(return_value=([], 0))
    dao.get_by_pk = AsyncMock(return_value=None)
    dao.create = AsyncMock()
    dao.update = AsyncMock()
    dao.delete = AsyncMock()

    return dao


@pytest.fixture
def test_client(mock_shop_dao, mock_user, test_config):
    """Create a test client with mocked dependencies.

    Shop routes are split across ``all_users`` and ``admin_only``; each module
    imports ``ShopDAO`` locally, so we patch both names to return the same
    mock and override ``get_db`` with a stand-in client.

    Args:
        mock_shop_dao: Mocked ShopDAO instance.
        mock_user: Mocked authenticated user.
        test_config: Test configuration fixture.

    Returns:
        TestClient: FastAPI test client with overridden dependencies.

    """
    app = get_app(test_config)

    app.dependency_overrides[user_authorized] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: MagicMock()

    with ExitStack() as stack:
        for path in _SHOP_DAO_PATHS:
            stack.enter_context(patch(path, return_value=mock_shop_dao))
        client = TestClient(app)
        yield client

    app.dependency_overrides.clear()


@pytest.mark.api
class TestGetShopList:
    """Test GET /api/v1/shop endpoint."""

    def test_get_shop_list_success(self, test_client, mock_shop_dao):
        """Test successful retrieval of shop list."""
        # Arrange
        mock_shop1 = MagicMock()
        mock_shop1.id = 1
        mock_shop1.name = "SuperMart"
        mock_shop1.icon = "supermart-icon.png"
        mock_shop1.description = "SuperMart description"
        mock_shop1.category_id = None
        mock_shop1.category = None

        mock_shop2 = MagicMock()
        mock_shop2.id = 2
        mock_shop2.name = "MegaStore"
        mock_shop2.icon = "megastore-icon.png"
        mock_shop2.description = "MegaStore description"
        mock_shop2.category_id = None
        mock_shop2.category = None

        mock_shops = [mock_shop1, mock_shop2]
        mock_shop_dao.get_all.return_value = (mock_shops, 2)

        # Act
        response = test_client.get("/api/v1/shop?limit=10&offset=0")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "metadata" in data
        assert len(data["data"]) == 2
        assert data["metadata"]["total"] == 2

    def test_get_shop_list_db_error(self, test_client, mock_shop_dao):
        """Test shop list with database error."""
        # Arrange
        mock_shop_dao.get_all.side_effect = DatabaseError("SELECT *", None, Exception("Database error"))

        # Act
        response = test_client.get("/api/v1/shop")

        # Assert
        assert response.status_code == 500


@pytest.mark.api
class TestGetShopById:
    """Test GET /api/v1/shop/{shop_id} endpoint."""

    def test_get_shop_by_id_success(self, test_client, mock_shop_dao):
        """Test successful retrieval of a single shop."""
        # Arrange
        shop_id = 42
        mock_shop = MagicMock()
        mock_shop.id = shop_id
        mock_shop.name = "Test Shop"
        mock_shop.icon = "test-icon.png"
        mock_shop.description = "Test description"
        mock_shop.category_id = None
        mock_shop.category = None
        mock_shop_dao.get_by_pk.return_value = mock_shop

        # Act
        response = test_client.get(f"/api/v1/shop/{shop_id}")

        # Assert
        assert response.status_code == 200
        mock_shop_dao.get_by_pk.assert_called_once_with(shop_id)

    def test_get_shop_by_id_not_found(self, test_client, mock_shop_dao):
        """Test retrieval of non-existent shop."""
        # Arrange
        mock_shop_dao.get_by_pk.side_effect = NoResultFound("Shop not found")

        # Act
        response = test_client.get("/api/v1/shop/999")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_shop_by_id_db_error(self, test_client, mock_shop_dao):
        """Test shop retrieval with database error."""
        # Arrange
        mock_shop_dao.get_by_pk.side_effect = DatabaseError("SELECT *", None, Exception("Database error"))

        # Act
        response = test_client.get("/api/v1/shop/42")

        # Assert
        assert response.status_code == 500


@pytest.mark.api
class TestCreateShop:
    """Test POST /api/v1/shop endpoint."""

    def test_create_shop_success(self, test_client, mock_shop_dao):
        """Test successful shop creation."""
        # Arrange
        new_shop = MagicMock()
        new_shop.id = 1
        new_shop.name = "New Shop"
        new_shop.icon = "new-icon.png"
        new_shop.description = "New description"
        new_shop.category_id = None
        new_shop.category = None
        mock_shop_dao.create.return_value = new_shop

        payload = {
            "name": "New Shop",
            "icon": "new-icon.png",
            "description": "New description",
        }

        # Act
        response = test_client.post("/api/v1/shop", json=payload)

        # Assert
        assert response.status_code == 201
        mock_shop_dao.create.assert_called_once()

    def test_create_shop_category_not_found(self, test_client, mock_shop_dao):
        """Test shop creation with invalid category ID."""
        # Arrange
        mock_shop_dao.create.side_effect = IntegrityError("INSERT INTO", None, Exception("Category not found"))

        payload = {
            "name": "New Shop",
            "icon": "new-icon.png",
            "description": "New description",
            "category_id": 999,
        }

        # Act
        response = test_client.post("/api/v1/shop", json=payload)

        # Assert
        assert response.status_code == 400
        assert "Related object not found" in response.json()["detail"]

    def test_create_shop_db_error(self, test_client, mock_shop_dao):
        """Test shop creation with database error."""
        # Arrange
        mock_shop_dao.create.side_effect = DatabaseError("SELECT *", None, Exception("Database error"))

        payload = {
            "name": "New Shop",
            "icon": "new-icon.png",
            "description": "New description",
        }

        # Act
        response = test_client.post("/api/v1/shop", json=payload)

        # Assert
        assert response.status_code == 500


@pytest.mark.api
class TestUpdateShop:
    """Test PUT /api/v1/shop/{shop_id} endpoint."""

    def test_update_shop_success(self, test_client, mock_shop_dao):
        """Test successful shop update."""
        # Arrange
        shop_id = 42
        updated_shop = MagicMock()
        updated_shop.id = shop_id
        updated_shop.name = "Updated Shop"
        updated_shop.icon = "updated-icon.png"
        updated_shop.description = "Updated description"
        updated_shop.category_id = None
        updated_shop.category = None
        mock_shop_dao.update.return_value = updated_shop

        payload = {
            "name": "Updated Shop",
            "icon": "updated-icon.png",
            "description": "Updated description",
        }

        # Act
        response = test_client.put(f"/api/v1/shop/{shop_id}", json=payload)

        # Assert
        assert response.status_code == 200
        mock_shop_dao.update.assert_called_once()

    def test_update_shop_not_found(self, test_client, mock_shop_dao):
        """Test updating non-existent shop."""
        # Arrange
        mock_shop_dao.update.side_effect = NoResultFound("Shop not found")

        payload = {
            "name": "Updated Shop",
            "icon": "updated-icon.png",
            "description": "Updated description",
        }

        # Act
        response = test_client.put("/api/v1/shop/999", json=payload)

        # Assert
        assert response.status_code == 404

    def test_update_shop_category_not_found(self, test_client, mock_shop_dao):
        """Test shop update with invalid category ID."""
        # Arrange
        mock_shop_dao.update.side_effect = IntegrityError("INSERT INTO", None, Exception("Category not found"))

        payload = {
            "name": "Updated Shop",
            "icon": "updated-icon.png",
            "description": "Updated description",
            "category_id": 999,
        }

        # Act
        response = test_client.put("/api/v1/shop/42", json=payload)

        # Assert
        assert response.status_code == 400


@pytest.mark.api
class TestDeleteShop:
    """Test DELETE /api/v1/shop/{shop_id} endpoint."""

    def test_delete_shop_success(self, test_client, mock_shop_dao):
        """Test successful shop deletion."""
        # Arrange
        shop_id = 42
        mock_shop_dao.delete.return_value = True

        # Act
        response = test_client.delete(f"/api/v1/shop/{shop_id}")

        # Assert
        assert response.status_code == 204
        mock_shop_dao.delete.assert_called_once_with(shop_id)

    def test_delete_shop_not_found(self, test_client, mock_shop_dao):
        """Test deleting non-existent shop."""
        # Arrange
        mock_shop_dao.delete.side_effect = NoResultFound("Shop not found")

        # Act
        response = test_client.delete("/api/v1/shop/999")

        # Assert
        assert response.status_code == 404

    def test_delete_shop_db_error(self, test_client, mock_shop_dao):
        """Test shop deletion with database error."""
        # Arrange
        mock_shop_dao.delete.side_effect = DatabaseError("SELECT *", None, Exception("Database error"))

        # Act
        response = test_client.delete("/api/v1/shop/42")

        # Assert
        assert response.status_code == 500
