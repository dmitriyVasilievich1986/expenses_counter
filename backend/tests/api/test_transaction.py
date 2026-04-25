"""API tests for transaction endpoints.

This module tests all transaction API endpoints without making direct database calls.
It uses FastAPI's TestClient and mocks the TransactionDAO dependency.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import DatabaseError, IntegrityError, NoResultFound

from expenses_counter.modules.app import get_app
from expenses_counter.modules.middlewares.dependencies.daos import get_transaction


@pytest.fixture
def mock_transaction_dao():
    """Create a mock TransactionDAO for testing.

    Returns:
        AsyncMock: Mocked TransactionDAO instance that works as a context manager.

    """
    dao = AsyncMock()
    dao.get_all = AsyncMock(return_value=([], 0))
    dao.get_by_pk = AsyncMock(return_value=None)
    dao.create = AsyncMock()
    dao.update = AsyncMock()
    dao.delete = AsyncMock()

    # Make it work as a context manager
    dao.__aenter__ = AsyncMock(return_value=dao)
    dao.__aexit__ = AsyncMock(return_value=None)

    return dao


@pytest.fixture
def test_client(mock_transaction_dao, test_config):
    """Create a test client with mocked dependencies.

    Args:
        mock_transaction_dao: Mocked TransactionDAO instance.
        test_config: Test configuration fixture.

    Returns:
        TestClient: FastAPI test client with overridden dependencies.

    """
    app = get_app(test_config)

    app.dependency_overrides[get_transaction] = lambda: mock_transaction_dao

    client = TestClient(app)
    yield client

    # Clean up
    app.dependency_overrides.clear()


@pytest.mark.api
class TestGetTransactionsByDateRange:
    """Test POST /api/v1/transaction/monthly endpoint."""

    def test_get_transactions_by_date_range_success(self, test_client, mock_transaction_dao):
        """Test successful retrieval of transactions by date range."""
        # Arrange
        # Create mock product
        mock_product = MagicMock()
        mock_product.id = 1
        mock_product.name = "Test Product"
        mock_product.description = "Test product description"
        mock_product.category_id = 1

        # Create mock address
        mock_address = MagicMock()
        mock_address.id = 1
        mock_address.local_name = "Test Store"
        mock_address.address = "123 Test St"

        mock_transaction1 = MagicMock()
        mock_transaction1.id = 1
        mock_transaction1.date = datetime(2024, 1, 15)
        mock_transaction1.count = 2
        mock_transaction1.price = 10.50
        mock_transaction1.product_id = 1
        mock_transaction1.address_id = 1
        mock_transaction1.product = mock_product
        mock_transaction1.address = mock_address

        mock_transaction2 = MagicMock()
        mock_transaction2.id = 2
        mock_transaction2.date = datetime(2024, 1, 20)
        mock_transaction2.count = 1
        mock_transaction2.price = 5.00
        mock_transaction2.product_id = 1
        mock_transaction2.address_id = 1
        mock_transaction2.product = mock_product
        mock_transaction2.address = mock_address

        mock_transactions = [mock_transaction1, mock_transaction2]
        mock_transaction_dao.get_all.return_value = (mock_transactions, 2)

        payload = {
            "date": "2024-01-15",
        }

        # Act
        response = test_client.post("/api/v1/transaction/monthly", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "metadata" in data
        assert len(data["data"]) == 2
        mock_transaction_dao.get_all.assert_called_once()

    def test_get_transactions_by_date_range_db_error(self, test_client, mock_transaction_dao):
        """Test transactions by date range with database error."""
        # Arrange
        mock_transaction_dao.get_all.side_effect = DatabaseError("SELECT *", None, Exception("Database error"))

        payload = {
            "date": "2024-01-15",
        }

        # Act
        response = test_client.post("/api/v1/transaction/monthly", json=payload)

        # Assert
        assert response.status_code == 500


@pytest.mark.api
class TestGetTransactionList:
    """Test GET /api/v1/transaction endpoint."""

    def test_get_transaction_list_success(self, test_client, mock_transaction_dao):
        """Test successful retrieval of transaction list."""
        # Arrange
        # Create mock product
        mock_product = MagicMock()
        mock_product.id = 1
        mock_product.name = "Test Product"
        mock_product.description = "Test product description"
        mock_product.category_id = 1

        # Create mock address
        mock_address = MagicMock()
        mock_address.id = 1
        mock_address.local_name = "Test Store"
        mock_address.address = "123 Test St"

        mock_transaction1 = MagicMock()
        mock_transaction1.id = 1
        mock_transaction1.date = datetime(2024, 1, 15)
        mock_transaction1.count = 2
        mock_transaction1.price = 10.50
        mock_transaction1.product_id = 1
        mock_transaction1.address_id = 1
        mock_transaction1.product = mock_product
        mock_transaction1.address = mock_address

        mock_transaction2 = MagicMock()
        mock_transaction2.id = 2
        mock_transaction2.date = datetime(2024, 1, 20)
        mock_transaction2.count = 1
        mock_transaction2.price = 5.00
        mock_transaction2.product_id = 1
        mock_transaction2.address_id = 1
        mock_transaction2.product = mock_product
        mock_transaction2.address = mock_address

        mock_transactions = [mock_transaction1, mock_transaction2]
        mock_transaction_dao.get_all.return_value = (mock_transactions, 2)

        # Act
        response = test_client.get("/api/v1/transaction?limit=10&offset=0")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "metadata" in data
        assert len(data["data"]) == 2
        assert data["metadata"]["total"] == 2

    def test_get_transaction_list_db_error(self, test_client, mock_transaction_dao):
        """Test transaction list with database error."""
        # Arrange
        mock_transaction_dao.get_all.side_effect = DatabaseError("SELECT *", None, Exception("Database error"))

        # Act
        response = test_client.get("/api/v1/transaction")

        # Assert
        assert response.status_code == 500


@pytest.mark.api
class TestGetTransactionById:
    """Test GET /api/v1/transaction/{transaction_id} endpoint."""

    def test_get_transaction_by_id_success(self, test_client, mock_transaction_dao):
        """Test successful retrieval of a single transaction."""
        # Arrange
        transaction_id = 42

        # Create mock product
        mock_product = MagicMock()
        mock_product.id = 1
        mock_product.name = "Test Product"
        mock_product.description = "Test product description"
        mock_product.category_id = 1

        # Create mock address
        mock_address = MagicMock()
        mock_address.id = 1
        mock_address.local_name = "Test Store"
        mock_address.address = "123 Test St"

        mock_transaction = MagicMock()
        mock_transaction.id = transaction_id
        mock_transaction.date = datetime(2024, 1, 15)
        mock_transaction.count = 2
        mock_transaction.price = 10.50
        mock_transaction.product_id = 1
        mock_transaction.address_id = 1
        mock_transaction.product = mock_product
        mock_transaction.address = mock_address
        mock_transaction_dao.get_by_pk.return_value = mock_transaction

        # Act
        response = test_client.get(f"/api/v1/transaction/{transaction_id}")

        # Assert
        assert response.status_code == 200
        mock_transaction_dao.get_by_pk.assert_called_once_with(transaction_id)

    def test_get_transaction_by_id_not_found(self, test_client, mock_transaction_dao):
        """Test retrieval of non-existent transaction."""
        # Arrange
        mock_transaction_dao.get_by_pk.side_effect = NoResultFound("Transaction not found")

        # Act
        response = test_client.get("/api/v1/transaction/999")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_transaction_by_id_db_error(self, test_client, mock_transaction_dao):
        """Test transaction retrieval with database error."""
        # Arrange
        mock_transaction_dao.get_by_pk.side_effect = DatabaseError("SELECT *", None, Exception("Database error"))

        # Act
        response = test_client.get("/api/v1/transaction/42")

        # Assert
        assert response.status_code == 500


@pytest.mark.api
class TestCreateTransaction:
    """Test POST /api/v1/transaction endpoint."""

    def test_create_transaction_success(self, test_client, mock_transaction_dao):
        """Test successful transaction creation."""
        # Arrange
        # Create mock product
        mock_product = MagicMock()
        mock_product.id = 1
        mock_product.name = "Test Product"
        mock_product.description = "Test product description"
        mock_product.category_id = 1

        # Create mock address
        mock_address = MagicMock()
        mock_address.id = 1
        mock_address.local_name = "Test Store"
        mock_address.address = "123 Test St"

        new_transaction = MagicMock()
        new_transaction.id = 1
        new_transaction.date = datetime(2024, 1, 15)
        new_transaction.count = 2
        new_transaction.price = 10.50
        new_transaction.product_id = 1
        new_transaction.address_id = 1
        new_transaction.product = mock_product
        new_transaction.address = mock_address
        mock_transaction_dao.create.return_value = new_transaction

        payload = {
            "date": "2024-01-15",
            "count": 2,
            "price": 10.50,
            "productId": 1,
            "addressId": 1,
        }

        # Act
        response = test_client.post("/api/v1/transaction", json=payload)

        # Assert
        assert response.status_code == 201
        mock_transaction_dao.create.assert_called_once()

    def test_create_transaction_relationship_not_found(self, test_client, mock_transaction_dao):
        """Test transaction creation with invalid product or address ID."""
        # Arrange
        mock_transaction_dao.create.side_effect = IntegrityError(
            "INSERT INTO", None, Exception("Product or Address not found")
        )

        payload = {
            "date": "2024-01-15",
            "count": 2,
            "price": 10.50,
            "productId": 999,
            "addressId": 1,
        }

        # Act
        response = test_client.post("/api/v1/transaction", json=payload)

        # Assert
        assert response.status_code == 400
        assert "Related object not found" in response.json()["detail"]

    def test_create_transaction_db_error(self, test_client, mock_transaction_dao):
        """Test transaction creation with database error."""
        # Arrange
        mock_transaction_dao.create.side_effect = DatabaseError("SELECT *", None, Exception("Database error"))

        payload = {
            "date": "2024-01-15",
            "count": 2,
            "price": 10.50,
            "productId": 1,
            "addressId": 1,
        }

        # Act
        response = test_client.post("/api/v1/transaction", json=payload)

        # Assert
        assert response.status_code == 500


@pytest.mark.api
class TestUpdateTransaction:
    """Test PUT /api/v1/transaction/{transaction_id} endpoint."""

    def test_update_transaction_success(self, test_client, mock_transaction_dao):
        """Test successful transaction update."""
        # Arrange
        transaction_id = 42

        # Create mock product
        mock_product = MagicMock()
        mock_product.id = 1
        mock_product.name = "Test Product"
        mock_product.description = "Test product description"
        mock_product.category_id = 1

        # Create mock address
        mock_address = MagicMock()
        mock_address.id = 1
        mock_address.local_name = "Test Store"
        mock_address.address = "123 Test St"

        updated_transaction = MagicMock()
        updated_transaction.id = transaction_id
        updated_transaction.date = datetime(2024, 1, 16)
        updated_transaction.count = 3
        updated_transaction.price = 15.00
        updated_transaction.product_id = 1
        updated_transaction.address_id = 1
        updated_transaction.product = mock_product
        updated_transaction.address = mock_address
        mock_transaction_dao.update.return_value = updated_transaction

        payload = {
            "date": "2024-01-16",
            "count": 3,
            "price": 15.00,
            "productId": 1,
            "addressId": 1,
        }

        # Act
        response = test_client.put(f"/api/v1/transaction/{transaction_id}", json=payload)

        # Assert
        assert response.status_code == 200
        mock_transaction_dao.update.assert_called_once()

    def test_update_transaction_not_found(self, test_client, mock_transaction_dao):
        """Test updating non-existent transaction."""
        # Arrange
        mock_transaction_dao.update.side_effect = NoResultFound("Transaction not found")

        payload = {
            "date": "2024-01-16",
            "count": 3,
            "price": 15.00,
            "productId": 1,
            "addressId": 1,
        }

        # Act
        response = test_client.put("/api/v1/transaction/999", json=payload)

        # Assert
        assert response.status_code == 404

    def test_update_transaction_relationship_not_found(self, test_client, mock_transaction_dao):
        """Test transaction update with invalid product or address ID."""
        # Arrange
        mock_transaction_dao.update.side_effect = IntegrityError(
            "INSERT INTO", None, Exception("Product or Address not found")
        )

        payload = {
            "date": "2024-01-16",
            "count": 3,
            "price": 15.00,
            "productId": 999,
            "addressId": 1,
        }

        # Act
        response = test_client.put("/api/v1/transaction/42", json=payload)

        # Assert
        assert response.status_code == 400


@pytest.mark.api
class TestDeleteTransaction:
    """Test DELETE /api/v1/transaction/{transaction_id} endpoint."""

    def test_delete_transaction_success(self, test_client, mock_transaction_dao):
        """Test successful transaction deletion."""
        # Arrange
        transaction_id = 42
        mock_transaction_dao.delete.return_value = True

        # Act
        response = test_client.delete(f"/api/v1/transaction/{transaction_id}")

        # Assert
        assert response.status_code == 204
        mock_transaction_dao.delete.assert_called_once_with(transaction_id)

    def test_delete_transaction_not_found(self, test_client, mock_transaction_dao):
        """Test deleting non-existent transaction."""
        # Arrange
        mock_transaction_dao.delete.side_effect = NoResultFound("Transaction not found")

        # Act
        response = test_client.delete("/api/v1/transaction/999")

        # Assert
        assert response.status_code == 404

    def test_delete_transaction_db_error(self, test_client, mock_transaction_dao):
        """Test transaction deletion with database error."""
        # Arrange
        mock_transaction_dao.delete.side_effect = DatabaseError("SELECT *", None, Exception("Database error"))

        # Act
        response = test_client.delete("/api/v1/transaction/42")

        # Assert
        assert response.status_code == 500
