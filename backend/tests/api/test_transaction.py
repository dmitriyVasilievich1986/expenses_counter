"""API tests for transaction endpoints.

This module tests all transaction API endpoints without making direct database calls.
It uses FastAPI's TestClient and patches the ``TransactionDAO`` class so that the
router-instantiated DAO is the same mock the tests configure.
"""

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import DatabaseError, IntegrityError, NoResultFound

from expenses_counter.modules.app import get_app
from expenses_counter.modules.middlewares.dependencies import get_db, user_authorized


@pytest.fixture
def mock_transaction_dao():
    """Create a mock TransactionDAO for testing.

    ``concat_filters`` is sync, so it must be a ``MagicMock`` rather than the
    default ``AsyncMock`` child the parent would otherwise create.

    Returns:
        AsyncMock: Mocked TransactionDAO instance.

    """
    dao = AsyncMock()
    dao.get_all = AsyncMock(return_value=([], 0))
    dao.get_by_pk = AsyncMock(return_value=None)
    dao.create = AsyncMock()
    dao.update = AsyncMock()
    dao.delete = AsyncMock()
    dao.concat_filters = MagicMock(return_value=[])

    return dao


@pytest.fixture
def test_client(mock_transaction_dao, mock_user, test_config):
    """Create a test client with mocked dependencies.

    The route instantiates ``TransactionDAO`` directly, so we patch the class
    in the router module to return the same mock and override ``get_db`` with
    a stand-in database client.

    Args:
        mock_transaction_dao: Mocked TransactionDAO instance.
        mock_user: Mocked authenticated user.
        test_config: Test configuration fixture.

    Returns:
        TestClient: FastAPI test client with overridden dependencies.

    """
    app = get_app(test_config)

    app.dependency_overrides[user_authorized] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: MagicMock()

    with patch(
        "expenses_counter.modules.routers.api.v1.transaction.TransactionDAO",
        return_value=mock_transaction_dao,
    ):
        client = TestClient(app)
        yield client

    app.dependency_overrides.clear()


@pytest.mark.api
class TestGetTransactionList:
    """Test GET /api/v1/transaction endpoint."""

    def test_get_transaction_list_success(self, test_client, mock_transaction_dao):
        """Test successful retrieval of transaction list."""
        mock_product = MagicMock()
        mock_product.id = 1
        mock_product.name = "Test Product"
        mock_product.description = "Test product description"
        mock_product.category_id = 1

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

        response = test_client.get("/api/v1/transaction?limit=10&offset=0")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "metadata" in data
        assert len(data["data"]) == 2
        assert data["metadata"]["total"] == 2

    def test_get_transaction_list_db_error(self, test_client, mock_transaction_dao):
        """Test transaction list with database error."""
        mock_transaction_dao.get_all.side_effect = DatabaseError("SELECT *", None, Exception("Database error"))

        response = test_client.get("/api/v1/transaction")

        assert response.status_code == 500


@pytest.mark.api
class TestGetTransactionById:
    """Test GET /api/v1/transaction/{transaction_id} endpoint."""

    def test_get_transaction_by_id_success(self, test_client, mock_transaction_dao):
        """Test successful retrieval of a single transaction."""
        transaction_id = 42

        mock_product = MagicMock()
        mock_product.id = 1
        mock_product.name = "Test Product"
        mock_product.description = "Test product description"
        mock_product.category_id = 1

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

        response = test_client.get(f"/api/v1/transaction/{transaction_id}")

        assert response.status_code == 200
        mock_transaction_dao.get_by_pk.assert_called_once()
        assert mock_transaction_dao.get_by_pk.call_args.args[0] == transaction_id

    def test_get_transaction_by_id_not_found(self, test_client, mock_transaction_dao):
        """Test retrieval of non-existent transaction."""
        mock_transaction_dao.get_by_pk.side_effect = NoResultFound("Transaction not found")

        response = test_client.get("/api/v1/transaction/999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_transaction_by_id_db_error(self, test_client, mock_transaction_dao):
        """Test transaction retrieval with database error."""
        mock_transaction_dao.get_by_pk.side_effect = DatabaseError("SELECT *", None, Exception("Database error"))

        response = test_client.get("/api/v1/transaction/42")

        assert response.status_code == 500


@pytest.mark.api
class TestCreateTransaction:
    """Test POST /api/v1/transaction endpoint."""

    def test_create_transaction_success(self, test_client, mock_transaction_dao):
        """Test successful transaction creation."""
        mock_product = MagicMock()
        mock_product.id = 1
        mock_product.name = "Test Product"
        mock_product.description = "Test product description"
        mock_product.category_id = 1

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

        response = test_client.post("/api/v1/transaction", json=payload)

        assert response.status_code == 201
        mock_transaction_dao.create.assert_called_once()

    def test_create_transaction_relationship_not_found(self, test_client, mock_transaction_dao):
        """Test transaction creation with invalid product or address ID."""
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

        response = test_client.post("/api/v1/transaction", json=payload)

        assert response.status_code == 400
        assert "Related object not found" in response.json()["detail"]

    def test_create_transaction_db_error(self, test_client, mock_transaction_dao):
        """Test transaction creation with database error."""
        mock_transaction_dao.create.side_effect = DatabaseError("SELECT *", None, Exception("Database error"))

        payload = {
            "date": "2024-01-15",
            "count": 2,
            "price": 10.50,
            "productId": 1,
            "addressId": 1,
        }

        response = test_client.post("/api/v1/transaction", json=payload)

        assert response.status_code == 500


@pytest.mark.api
class TestUpdateTransaction:
    """Test PUT /api/v1/transaction/{transaction_id} endpoint."""

    def test_update_transaction_success(self, test_client, mock_transaction_dao):
        """Test successful transaction update."""
        transaction_id = 42

        mock_product = MagicMock()
        mock_product.id = 1
        mock_product.name = "Test Product"
        mock_product.description = "Test product description"
        mock_product.category_id = 1

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

        response = test_client.put(f"/api/v1/transaction/{transaction_id}", json=payload)

        assert response.status_code == 200
        mock_transaction_dao.update.assert_called_once()

    def test_update_transaction_not_found(self, test_client, mock_transaction_dao):
        """Test updating non-existent transaction."""
        mock_transaction_dao.update.side_effect = NoResultFound("Transaction not found")

        payload = {
            "date": "2024-01-16",
            "count": 3,
            "price": 15.00,
            "productId": 1,
            "addressId": 1,
        }

        response = test_client.put("/api/v1/transaction/999", json=payload)

        assert response.status_code == 404

    def test_update_transaction_relationship_not_found(self, test_client, mock_transaction_dao):
        """Test transaction update with invalid product or address ID."""
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

        response = test_client.put("/api/v1/transaction/42", json=payload)

        assert response.status_code == 400


@pytest.mark.api
class TestDeleteTransaction:
    """Test DELETE /api/v1/transaction/{transaction_id} endpoint."""

    def test_delete_transaction_success(self, test_client, mock_transaction_dao):
        """Test successful transaction deletion."""
        transaction_id = 42
        mock_transaction_dao.delete.return_value = True

        response = test_client.delete(f"/api/v1/transaction/{transaction_id}")

        assert response.status_code == 204
        mock_transaction_dao.delete.assert_called_once()
        assert mock_transaction_dao.delete.call_args.args[0] == transaction_id

    def test_delete_transaction_not_found(self, test_client, mock_transaction_dao):
        """Test deleting non-existent transaction."""
        mock_transaction_dao.delete.side_effect = NoResultFound("Transaction not found")

        response = test_client.delete("/api/v1/transaction/999")

        assert response.status_code == 404

    def test_delete_transaction_db_error(self, test_client, mock_transaction_dao):
        """Test transaction deletion with database error."""
        mock_transaction_dao.delete.side_effect = DatabaseError("SELECT *", None, Exception("Database error"))

        response = test_client.delete("/api/v1/transaction/42")

        assert response.status_code == 500


@pytest.mark.api
class TestGetTransactionListFilters:
    """Test GET /api/v1/transaction with filters query param.

    The route forwards ``query.filters_dict`` together with a user-scope filter
    into ``concat_filters``, then passes the resulting list to ``get_all``.
    """

    def test_get_transaction_list_with_eq_filter(self, test_client, mock_transaction_dao):
        """A dict filter from the query string reaches ``concat_filters`` and ``get_all``."""
        mock_transaction_dao.get_all.return_value = ([], 0)
        filters = [{"column": "price", "operator": "ge", "value": 10.0}]

        response = test_client.get("/api/v1/transaction", params={"filters": json.dumps(filters)})

        assert response.status_code == 200
        forwarded = mock_transaction_dao.concat_filters.call_args.args[0]
        assert len(forwarded) == 1
        assert forwarded[0].column == "price"
        assert forwarded[0].operator == "ge"
        assert forwarded[0].value == 10.0
        get_all_kwargs = mock_transaction_dao.get_all.call_args.kwargs
        assert get_all_kwargs["filters"] is mock_transaction_dao.concat_filters.return_value

    def test_get_transaction_list_without_filters_passes_empty_list(self, test_client, mock_transaction_dao):
        """Omitted filters produce an empty list from ``filters_dict`` for ``concat_filters``."""
        mock_transaction_dao.get_all.return_value = ([], 0)

        response = test_client.get("/api/v1/transaction")

        assert response.status_code == 200
        forwarded = mock_transaction_dao.concat_filters.call_args.args[0]
        assert forwarded == []
        get_all_kwargs = mock_transaction_dao.get_all.call_args.kwargs
        assert get_all_kwargs["filters"] is mock_transaction_dao.concat_filters.return_value

    def test_get_transaction_list_with_multiple_filters(self, test_client, mock_transaction_dao):
        """Multiple filters from the query string are all forwarded to ``concat_filters``."""
        mock_transaction_dao.get_all.return_value = ([], 0)
        filters = [
            {"column": "price", "operator": "ge", "value": 5.0},
            {"column": "price", "operator": "le", "value": 100.0},
        ]

        response = test_client.get("/api/v1/transaction", params={"filters": json.dumps(filters)})

        assert response.status_code == 200
        forwarded = mock_transaction_dao.concat_filters.call_args.args[0]
        assert len(forwarded) == 2
        assert (forwarded[0].operator, forwarded[0].value) == ("ge", 5.0)
        assert (forwarded[1].operator, forwarded[1].value) == ("le", 100.0)
