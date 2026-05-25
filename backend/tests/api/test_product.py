"""API tests for product endpoints.

This module tests all product API endpoints without making direct database calls.
It uses FastAPI's TestClient and mocks the ProductDAO dependency.
"""

from contextlib import ExitStack
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import DatabaseError, IntegrityError, NoResultFound

from expenses_counter.modules.app import get_app
from expenses_counter.modules.middlewares.dependencies import get_db, user_authorized

_PRODUCT_DAO_PATHS = (
    "expenses_counter.modules.routers.api.v1.product.all_users.ProductDAO",
    "expenses_counter.modules.routers.api.v1.product.admin_only.ProductDAO",
)


@pytest.fixture
def mock_product_dao():
    """Create a mock ProductDAO for testing.

    Returns:
        AsyncMock: Mocked ProductDAO instance.

    """
    dao = AsyncMock()
    dao.get_all = AsyncMock(return_value=([], 0))
    dao.get_by_pk = AsyncMock(return_value=None)
    dao.create = AsyncMock()
    dao.update = AsyncMock()
    dao.delete = AsyncMock()

    return dao


@pytest.fixture
def test_client(mock_product_dao, mock_user, test_config):
    """Create a test client with mocked dependencies.

    Product routes are split across ``all_users`` and ``admin_only``; each
    module imports ``ProductDAO`` locally, so we patch both names to return
    the same mock and override ``get_db`` with a stand-in client.

    Args:
        mock_product_dao: Mocked ProductDAO instance.
        mock_user: Mocked authenticated user.
        test_config: Test configuration fixture.

    Returns:
        TestClient: FastAPI test client with overridden dependencies.

    """
    app = get_app(test_config)

    app.dependency_overrides[user_authorized] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: MagicMock()

    with ExitStack() as stack:
        for path in _PRODUCT_DAO_PATHS:
            stack.enter_context(patch(path, return_value=mock_product_dao))
        client = TestClient(app)
        yield client

    app.dependency_overrides.clear()


@pytest.mark.api
class TestGetProductList:
    """Test GET /api/v1/product endpoint."""

    def test_get_product_list_success(self, test_client, mock_product_dao):
        """Test successful retrieval of product list."""
        # Arrange
        mock_product1 = MagicMock()
        mock_product1.id = 1
        mock_product1.name = "Milk"
        mock_product1.description = "Fresh milk"
        mock_product1.category_id = 1

        mock_product2 = MagicMock()
        mock_product2.id = 2
        mock_product2.name = "Bread"
        mock_product2.description = "Whole wheat bread"
        mock_product2.category_id = 1

        mock_products = [mock_product1, mock_product2]
        mock_product_dao.get_all.return_value = (mock_products, 2)

        # Act
        response = test_client.get("/api/v1/product?limit=10&offset=0")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "metadata" in data
        assert len(data["data"]) == 2
        assert data["metadata"]["total"] == 2

    def test_get_product_list_db_error(self, test_client, mock_product_dao):
        """Test product list with database error."""
        # Arrange
        mock_product_dao.get_all.side_effect = DatabaseError("SELECT *", None, Exception("Database error"))

        # Act
        response = test_client.get("/api/v1/product")

        # Assert
        assert response.status_code == 500


@pytest.mark.api
class TestGetProductById:
    """Test GET /api/v1/product/{product_id} endpoint."""

    def test_get_product_by_id_success(self, test_client, mock_product_dao):
        """Test successful retrieval of a single product."""
        # Arrange
        product_id = 42
        mock_product = MagicMock()
        mock_product.id = product_id
        mock_product.name = "Test Product"
        mock_product.description = "Test description"
        mock_product.sub_category_id = 1
        mock_product.category = None
        mock_product.img_path = None
        mock_product_dao.get_by_pk.return_value = mock_product

        # Act
        response = test_client.get(f"/api/v1/product/{product_id}")

        # Assert
        assert response.status_code == 200
        mock_product_dao.get_by_pk.assert_called_once_with(product_id)

    def test_get_product_by_id_not_found(self, test_client, mock_product_dao):
        """Test retrieval of non-existent product."""
        # Arrange
        mock_product_dao.get_by_pk.side_effect = NoResultFound("Product not found")

        # Act
        response = test_client.get("/api/v1/product/999")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_product_by_id_db_error(self, test_client, mock_product_dao):
        """Test product retrieval with database error."""
        # Arrange
        mock_product_dao.get_by_pk.side_effect = DatabaseError("SELECT *", None, Exception("Database error"))

        # Act
        response = test_client.get("/api/v1/product/42")

        # Assert
        assert response.status_code == 500


@pytest.mark.api
class TestCreateProduct:
    """Test POST /api/v1/product endpoint."""

    def test_create_product_success(self, test_client, mock_product_dao):
        """Test successful product creation."""
        # Arrange
        new_product = MagicMock()
        new_product.id = 1
        new_product.name = "New Product"
        new_product.description = "New product description"
        new_product.category_id = 1
        new_product.category = None
        mock_product_dao.create.return_value = new_product

        payload = {
            "name": "New Product",
            "sub_category_id": 1,
        }

        # Act
        response = test_client.post("/api/v1/product", json=payload)

        # Assert
        assert response.status_code == 201
        mock_product_dao.create.assert_called_once()

    def test_create_product_category_not_found(self, test_client, mock_product_dao):
        """Test product creation with invalid category ID."""
        # Arrange
        mock_product_dao.create.side_effect = IntegrityError("INSERT INTO", None, Exception("Category not found"))

        payload = {
            "name": "New Product",
            "sub_category_id": 999,
        }

        # Act
        response = test_client.post("/api/v1/product", json=payload)

        # Assert
        assert response.status_code == 400
        assert "Related object not found" in response.json()["detail"]

    def test_create_product_db_error(self, test_client, mock_product_dao):
        """Test product creation with database error."""
        # Arrange
        mock_product_dao.create.side_effect = DatabaseError("SELECT *", None, Exception("Database error"))

        payload = {
            "name": "New Product",
            "sub_category_id": 1,
        }

        # Act
        response = test_client.post("/api/v1/product", json=payload)

        # Assert
        assert response.status_code == 500


@pytest.mark.api
class TestUpdateProduct:
    """Test PUT /api/v1/product/{product_id} endpoint."""

    def test_update_product_success(self, test_client, mock_product_dao):
        """Test successful product update."""
        # Arrange
        product_id = 42
        updated_product = MagicMock()
        updated_product.id = product_id
        updated_product.name = "Updated Product"
        updated_product.description = "Updated description"
        updated_product.category_id = 1
        updated_product.category = None
        mock_product_dao.update.return_value = updated_product

        payload = {
            "name": "Updated Product",
            "sub_category_id": 1,
        }

        # Act
        response = test_client.put(f"/api/v1/product/{product_id}", json=payload)

        # Assert
        assert response.status_code == 200
        mock_product_dao.update.assert_called_once()

    def test_update_product_not_found(self, test_client, mock_product_dao):
        """Test updating non-existent product."""
        # Arrange
        mock_product_dao.update.side_effect = NoResultFound("Product not found")

        payload = {
            "name": "Updated Product",
            "sub_category_id": 1,
        }

        # Act
        response = test_client.put("/api/v1/product/999", json=payload)

        # Assert
        assert response.status_code == 404

    def test_update_product_category_not_found(self, test_client, mock_product_dao):
        """Test product update with invalid category ID."""
        # Arrange
        mock_product_dao.update.side_effect = IntegrityError("INSERT INTO", None, Exception("Category not found"))

        payload = {
            "name": "Updated Product",
            "sub_category_id": 999,
        }

        # Act
        response = test_client.put("/api/v1/product/42", json=payload)

        # Assert
        assert response.status_code == 400


@pytest.mark.api
class TestDeleteProduct:
    """Test DELETE /api/v1/product/{product_id} endpoint."""

    def test_delete_product_success(self, test_client, mock_product_dao):
        """Test successful product deletion."""
        # Arrange
        product_id = 42
        mock_product_dao.delete.return_value = None

        # Act
        response = test_client.delete(f"/api/v1/product/{product_id}")

        # Assert
        assert response.status_code == 204
        mock_product_dao.delete.assert_called_once_with(product_id)

    def test_delete_product_not_found(self, test_client, mock_product_dao):
        """Test deleting non-existent product."""
        # Arrange
        mock_product_dao.delete.side_effect = NoResultFound("Product not found")

        # Act
        response = test_client.delete("/api/v1/product/999")

        # Assert
        assert response.status_code == 404

    def test_delete_product_db_error(self, test_client, mock_product_dao):
        """Test product deletion with database error."""
        # Arrange
        mock_product_dao.delete.side_effect = DatabaseError("SELECT *", None, Exception("Database error"))

        # Act
        response = test_client.delete("/api/v1/product/42")

        # Assert
        assert response.status_code == 500
