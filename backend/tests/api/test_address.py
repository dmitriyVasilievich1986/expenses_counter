"""API tests for address endpoints.

This module tests all address API endpoints without making direct database calls.
It uses FastAPI's TestClient and mocks the AddressDAO dependency.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import DatabaseError, IntegrityError, NoResultFound

from expenses_counter.modules.app import get_app
from expenses_counter.modules.middlewares.dependencies.get_db import get_db


@pytest.fixture
def mock_address_dao():
    """Create a mock AddressDAO for testing.

    Returns:
        AsyncMock: Mocked AddressDAO instance that works as a context manager.

    """
    dao = AsyncMock()
    dao.get_all = AsyncMock(return_value=([], 0))
    dao.get_by_id = AsyncMock(return_value=None)
    dao.create = AsyncMock()
    dao.update = AsyncMock()
    dao.delete = AsyncMock()

    # Make it work as a context manager
    dao.__aenter__ = AsyncMock(return_value=dao)
    dao.__aexit__ = AsyncMock(return_value=None)

    return dao


@pytest.fixture
def mock_db_client():
    """Create a mock AsyncDatabaseClient for testing.

    Returns:
        MagicMock: Mocked AsyncDatabaseClient instance.

    """
    return MagicMock()


@pytest.fixture
def mock_address_dao_class(mock_address_dao):
    """Patch AddressDAO class to return our mock instance.

    Args:
        mock_address_dao: Mocked AddressDAO instance.

    Yields:
        Mock: Patched AddressDAO class.

    """
    with patch(
        "expenses_counter.modules.routers.api.v1.address.AddressDAO", return_value=mock_address_dao
    ) as mock_class:
        yield mock_class


@pytest.fixture
def test_client(mock_address_dao_class, mock_db_client, test_config):  # noqa: ARG001
    """Create a test client with mocked dependencies.

    Args:
        mock_address_dao_class: Patched AddressDAO class fixture.
        mock_db_client: Mocked AsyncDatabaseClient fixture.
        test_config: Test configuration fixture.

    Returns:
        TestClient: FastAPI test client with overridden dependencies.

    """
    app = get_app(test_config)

    # Override the database dependency to return mock db client
    app.dependency_overrides[get_db] = lambda: mock_db_client

    client = TestClient(app)
    yield client

    # Clean up
    app.dependency_overrides.clear()


@pytest.mark.api
class TestGetAddressList:
    """Test GET /api/v1/address endpoint."""

    def test_get_address_list_success(self, test_client, mock_address_dao):
        """Test successful retrieval of address list."""
        # Arrange
        mock_address1 = MagicMock()
        mock_address1.id = 1
        mock_address1.local_name = "Main Store"
        mock_address1.address = "123 Main St"
        mock_address1.shop_id = 1
        mock_address1.shop = None

        mock_address2 = MagicMock()
        mock_address2.id = 2
        mock_address2.local_name = "Downtown Branch"
        mock_address2.address = "456 Central Ave"
        mock_address2.shop_id = 1
        mock_address2.shop = None

        mock_addresses = [mock_address1, mock_address2]
        mock_address_dao.get_all.return_value = (mock_addresses, 2)

        # Act
        response = test_client.get("/api/v1/address?limit=10&offset=0")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "metadata" in data
        assert len(data["data"]) == 2
        assert data["metadata"]["total"] == 2

    def test_get_address_list_db_error(self, test_client, mock_address_dao):
        """Test address list with database error."""
        # Arrange
        mock_address_dao.get_all.side_effect = DatabaseError("SELECT *", None, Exception("Database error"))

        # Act
        response = test_client.get("/api/v1/address")

        # Assert
        assert response.status_code == 500
        assert "Something went wrong" in response.json()["detail"]


@pytest.mark.api
class TestGetAddressById:
    """Test GET /api/v1/address/{address_id} endpoint."""

    def test_get_address_by_id_success(self, test_client, mock_address_dao):
        """Test successful retrieval of a single address."""
        # Arrange
        address_id = 42

        # Create mock shop
        mock_shop = MagicMock()
        mock_shop.id = 1
        mock_shop.name = "Test Shop"

        mock_address = MagicMock()
        mock_address.id = address_id
        mock_address.local_name = "Test Address"
        mock_address.address = "123 Test St"
        mock_address.shop_id = 1
        mock_address.shop = mock_shop
        mock_address_dao.get_by_id.return_value = mock_address

        # Act
        response = test_client.get(f"/api/v1/address/{address_id}")

        # Assert
        assert response.status_code == 200
        mock_address_dao.get_by_id.assert_called_once_with(address_id)

    def test_get_address_by_id_not_found(self, test_client, mock_address_dao):
        """Test retrieval of non-existent address."""
        # Arrange
        mock_address_dao.get_by_id.side_effect = NoResultFound("Address not found")

        # Act
        response = test_client.get("/api/v1/address/999")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_address_by_id_db_error(self, test_client, mock_address_dao):
        """Test address retrieval with database error."""
        # Arrange
        mock_address_dao.get_by_id.side_effect = DatabaseError("SELECT *", None, Exception("Database error"))

        # Act
        response = test_client.get("/api/v1/address/42")

        # Assert
        assert response.status_code == 500


@pytest.mark.api
class TestCreateAddress:
    """Test POST /api/v1/address endpoint."""

    def test_create_address_success(self, test_client, mock_address_dao):
        """Test successful address creation."""
        # Arrange
        # Create mock shop
        mock_shop = MagicMock()
        mock_shop.id = 1
        mock_shop.name = "Test Shop"

        new_address = MagicMock()
        new_address.id = 1
        new_address.local_name = "New Address"
        new_address.address = "789 New St"
        new_address.shop_id = 1
        new_address.shop = mock_shop
        mock_address_dao.create.return_value = new_address

        payload = {
            "localName": "New Address",
            "address": "789 New St",
            "shopId": 1,
        }

        # Act
        response = test_client.post("/api/v1/address", json=payload)

        # Assert
        assert response.status_code == 200
        mock_address_dao.create.assert_called_once()

    def test_create_address_shop_not_found(self, test_client, mock_address_dao):
        """Test address creation with invalid shop ID."""
        # Arrange
        mock_address_dao.create.side_effect = IntegrityError("INSERT INTO", None, Exception("Shop not found"))

        payload = {
            "localName": "New Address",
            "address": "789 New St",
            "shopId": 999,
        }

        # Act
        response = test_client.post("/api/v1/address", json=payload)

        # Assert
        assert response.status_code == 400
        assert "Shop not found" in response.json()["detail"]

    def test_create_address_db_error(self, test_client, mock_address_dao):
        """Test address creation with database error."""
        # Arrange
        mock_address_dao.create.side_effect = DatabaseError("SELECT *", None, Exception("Database error"))

        payload = {
            "localName": "New Address",
            "address": "789 New St",
            "shopId": 1,
        }

        # Act
        response = test_client.post("/api/v1/address", json=payload)

        # Assert
        assert response.status_code == 500


@pytest.mark.api
class TestUpdateAddress:
    """Test PUT /api/v1/address/{address_id} endpoint."""

    def test_update_address_success(self, test_client, mock_address_dao):
        """Test successful address update."""
        # Arrange
        address_id = 42

        # Create mock shop
        mock_shop = MagicMock()
        mock_shop.id = 1
        mock_shop.name = "Test Shop"

        updated_address = MagicMock()
        updated_address.id = address_id
        updated_address.local_name = "Updated Address"
        updated_address.address = "Updated St"
        updated_address.shop_id = 1
        updated_address.shop = mock_shop
        mock_address_dao.update.return_value = updated_address

        payload = {
            "localName": "Updated Address",
            "address": "Updated St",
            "shopId": 1,
        }

        # Act
        response = test_client.put(f"/api/v1/address/{address_id}", json=payload)

        # Assert
        assert response.status_code == 200
        mock_address_dao.update.assert_called_once()

    def test_update_address_not_found(self, test_client, mock_address_dao):
        """Test updating non-existent address."""
        # Arrange
        mock_address_dao.update.side_effect = NoResultFound("Address not found")

        payload = {
            "localName": "Updated Address",
            "address": "Updated St",
            "shopId": 1,
        }

        # Act
        response = test_client.put("/api/v1/address/999", json=payload)

        # Assert
        assert response.status_code == 404

    def test_update_address_shop_not_found(self, test_client, mock_address_dao):
        """Test address update with invalid shop ID."""
        # Arrange
        mock_address_dao.update.side_effect = IntegrityError("INSERT INTO", None, Exception("Shop not found"))

        payload = {
            "localName": "Updated Address",
            "address": "Updated St",
            "shopId": 999,
        }

        # Act
        response = test_client.put("/api/v1/address/42", json=payload)

        # Assert
        assert response.status_code == 400


@pytest.mark.api
class TestDeleteAddress:
    """Test DELETE /api/v1/address/{address_id} endpoint."""

    def test_delete_address_success(self, test_client, mock_address_dao):
        """Test successful address deletion."""
        # Arrange
        address_id = 42
        mock_address_dao.delete.return_value = True

        # Act
        response = test_client.delete(f"/api/v1/address/{address_id}")

        # Assert
        assert response.status_code == 204
        mock_address_dao.delete.assert_called_once_with(address_id)

    def test_delete_address_not_found(self, test_client, mock_address_dao):
        """Test deleting non-existent address."""
        # Arrange
        mock_address_dao.delete.side_effect = NoResultFound("Address not found")

        # Act
        response = test_client.delete("/api/v1/address/999")

        # Assert
        assert response.status_code == 404

    def test_delete_address_db_error(self, test_client, mock_address_dao):
        """Test address deletion with database error."""
        # Arrange
        mock_address_dao.delete.side_effect = DatabaseError("SELECT *", None, Exception("Database error"))

        # Act
        response = test_client.delete("/api/v1/address/42")

        # Assert
        assert response.status_code == 500
