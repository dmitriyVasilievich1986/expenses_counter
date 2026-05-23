"""API tests for category endpoints.

This module tests all category API endpoints without making direct database calls.
It uses FastAPI's TestClient and mocks the CategoryDAO dependency.
"""

import json
from contextlib import ExitStack
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import DatabaseError, IntegrityError, NoResultFound

from expenses_counter.modules.app import get_app
from expenses_counter.modules.middlewares.dependencies import get_db, user_authorized

_CATEGORY_DAO_PATHS = (
    "expenses_counter.modules.routers.api.v1.category.all_users.CategoryDAO",
    "expenses_counter.modules.routers.api.v1.category.admin_only.CategoryDAO",
)


@pytest.fixture
def mock_category_dao():
    """Create a mock CategoryDAO for testing.

    Returns:
        AsyncMock: Mocked CategoryDAO instance.

    """
    dao = AsyncMock()
    dao.get_all = AsyncMock(return_value=([], 0))
    dao.get_by_pk = AsyncMock(return_value=None)
    dao.create = AsyncMock()
    dao.update = AsyncMock()
    dao.delete = AsyncMock()

    return dao


@pytest.fixture
def test_client(mock_category_dao, mock_user, test_config):
    """Create a test client with mocked dependencies.

    Category routes are split across ``all_users`` and ``admin_only``; each
    module imports ``CategoryDAO`` locally, so we patch both names to return
    the same mock and override ``get_db`` with a stand-in client.

    Args:
        mock_category_dao: Mocked CategoryDAO instance.
        mock_user: Mocked authenticated user.
        test_config: Test configuration fixture.

    Returns:
        TestClient: FastAPI test client with overridden dependencies.

    """
    app = get_app(test_config)

    app.dependency_overrides[user_authorized] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: MagicMock()

    with ExitStack() as stack:
        for path in _CATEGORY_DAO_PATHS:
            stack.enter_context(patch(path, return_value=mock_category_dao))
        client = TestClient(app)
        yield client

    app.dependency_overrides.clear()


@pytest.mark.api
class TestGetCategoryList:
    """Test GET /api/v1/category endpoint."""

    def test_get_category_list_success(self, test_client, mock_category_dao):
        """Test successful retrieval of category list.

        Args:
            test_client: FastAPI test client fixture.
            mock_category_dao: Mocked CategoryDAO fixture.

        """
        # Arrange - Create mock objects with proper attributes
        mock_category1 = MagicMock()
        mock_category1.id = 1
        mock_category1.name = "Food"

        mock_category2 = MagicMock()
        mock_category2.id = 2
        mock_category2.name = "Transport"

        mock_categories = [mock_category1, mock_category2]
        mock_category_dao.get_all.return_value = (mock_categories, 2)

        # Act
        response = test_client.get("/api/v1/category?limit=10&offset=0")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "metadata" in data
        assert len(data["data"]) == 2
        assert data["metadata"]["total"] == 2
        assert data["metadata"]["limit"] == 10
        assert data["metadata"]["offset"] == 0
        mock_category_dao.get_all.assert_called_once_with(
            limit=10, offset=0, sort_by="id", sort_order="asc", filters=None
        )

    def test_get_category_list_with_pagination(self, test_client, mock_category_dao):
        """Test category list with pagination parameters.

        Args:
            test_client: FastAPI test client fixture.
            mock_category_dao: Mocked CategoryDAO fixture.

        """
        # Arrange
        mock_category_dao.get_all.return_value = ([], 0)

        # Act
        response = test_client.get("/api/v1/category", params={"limit": 50, "offset": 10})

        # Assert
        assert response.status_code == 200
        data = response.json()
        # Verify the response structure
        assert "metadata" in data
        assert "data" in data
        assert data["metadata"]["total"] == 0
        # Verify DAO was called with pagination
        mock_category_dao.get_all.assert_called_once()
        call_kwargs = mock_category_dao.get_all.call_args.kwargs
        assert call_kwargs["limit"] == 50
        assert call_kwargs["offset"] == 10

    def test_get_category_list_db_error(self, test_client, mock_category_dao):
        """Test category list with database error.

        Args:
            test_client: FastAPI test client fixture.
            mock_category_dao: Mocked CategoryDAO fixture.

        """
        # Arrange
        mock_category_dao.get_all.side_effect = DatabaseError("SELECT *", None, Exception("Database error"))

        # Act
        response = test_client.get("/api/v1/category")

        # Assert
        assert response.status_code == 500
        assert "Something went wrong" in response.json()["detail"]


@pytest.mark.api
class TestGetCategoryById:
    """Test GET /api/v1/category/{category_id} endpoint."""

    def test_get_category_by_id_success(self, test_client, mock_category_dao):
        """Test successful retrieval of a single category.

        Args:
            test_client: FastAPI test client fixture.
            mock_category_dao: Mocked CategoryDAO fixture.

        """
        # Arrange
        category_id = 42
        mock_category = MagicMock()
        mock_category.id = category_id
        mock_category.name = "Test Category"
        mock_category.description = "Test description"
        mock_category.parent_id = None
        mock_category.parent = None
        mock_category_dao.get_by_pk.return_value = mock_category

        # Act
        response = test_client.get(f"/api/v1/category/{category_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == category_id
        assert data["name"] == "Test Category"
        mock_category_dao.get_by_pk.assert_called_once_with(category_id)

    def test_get_category_by_id_not_found(self, test_client, mock_category_dao):
        """Test retrieval of non-existent category.

        Args:
            test_client: FastAPI test client fixture.
            mock_category_dao: Mocked CategoryDAO fixture.

        """
        # Arrange
        mock_category_dao.get_by_pk.side_effect = NoResultFound("Category not found")

        # Act
        response = test_client.get("/api/v1/category/999")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_category_by_id_db_error(self, test_client, mock_category_dao):
        """Test category retrieval with database error.

        Args:
            test_client: FastAPI test client fixture.
            mock_category_dao: Mocked CategoryDAO fixture.

        """
        # Arrange
        mock_category_dao.get_by_pk.side_effect = DatabaseError("SELECT *", None, Exception("Database error"))

        # Act
        response = test_client.get("/api/v1/category/42")

        # Assert
        assert response.status_code == 500
        assert "Something went wrong" in response.json()["detail"]


@pytest.mark.api
class TestCreateCategory:
    """Test POST /api/v1/category endpoint."""

    def test_create_category_success(self, test_client, mock_category_dao):
        """Test successful category creation.

        Args:
            test_client: FastAPI test client fixture.
            mock_category_dao: Mocked CategoryDAO fixture.

        """
        # Arrange
        new_category = MagicMock()
        new_category.id = 1
        new_category.name = "New Category"
        new_category.description = "New description"
        new_category.parent_id = None
        new_category.parent = None
        mock_category_dao.create.return_value = new_category

        payload = {
            "name": "New Category",
            "description": "New description",
            "parent_id": None,
        }

        # Act
        response = test_client.post("/api/v1/category", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Category"
        assert data["description"] == "New description"
        mock_category_dao.create.assert_called_once()

    def test_create_category_with_parent(self, test_client, mock_category_dao):
        """Test category creation with parent relationship.

        Args:
            test_client: FastAPI test client fixture.
            mock_category_dao: Mocked CategoryDAO fixture.

        """
        # Arrange
        parent_id = 5
        parent_category = MagicMock()
        parent_category.id = parent_id
        parent_category.name = "Parent Category"
        parent_category.description = "Parent description"
        parent_category.parent = None

        new_category = MagicMock()
        new_category.id = 10
        new_category.name = "Child Category"
        new_category.description = "Child description"
        new_category.parent_id = parent_id
        new_category.parent = parent_category
        mock_category_dao.create.return_value = new_category

        payload = {
            "name": "Child Category",
            "description": "Child description",
            "parent_id": parent_id,
        }

        # Act
        response = test_client.post("/api/v1/category", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Child Category"
        assert data["parent"] is not None
        assert data["parent"]["id"] == parent_id

    def test_create_category_parent_not_found(self, test_client, mock_category_dao):
        """Test category creation with invalid parent ID.

        Args:
            test_client: FastAPI test client fixture.
            mock_category_dao: Mocked CategoryDAO fixture.

        """
        # Arrange
        mock_category_dao.create.side_effect = IntegrityError("INSERT INTO", None, Exception("Parent not found"))

        payload = {
            "name": "New Category",
            "parent_id": 999,
        }

        # Act
        response = test_client.post("/api/v1/category", json=payload)

        # Assert
        assert response.status_code == 400
        assert "Related object not found" in response.json()["detail"]

    def test_create_category_db_error(self, test_client, mock_category_dao):
        """Test category creation with database error.

        Args:
            test_client: FastAPI test client fixture.
            mock_category_dao: Mocked CategoryDAO fixture.

        """
        # Arrange
        mock_category_dao.create.side_effect = DatabaseError("SELECT *", None, Exception("Database error"))

        payload = {"name": "New Category"}

        # Act
        response = test_client.post("/api/v1/category", json=payload)

        # Assert
        assert response.status_code == 500
        assert "creating" in response.json()["detail"].lower()

    def test_create_category_validation_error(self, test_client):
        """Test category creation with invalid data.

        Args:
            test_client: FastAPI test client fixture.

        """
        # Arrange - empty name should fail validation
        payload = {"name": ""}

        # Act
        response = test_client.post("/api/v1/category", json=payload)

        # Assert
        assert response.status_code == 422  # Validation error


@pytest.mark.api
class TestUpdateCategory:
    """Test PUT /api/v1/category/{category_id} endpoint."""

    def test_update_category_success(self, test_client, mock_category_dao):
        """Test successful category update.

        Args:
            test_client: FastAPI test client fixture.
            mock_category_dao: Mocked CategoryDAO fixture.

        """
        # Arrange
        category_id = 42
        updated_category = MagicMock()
        updated_category.id = category_id
        updated_category.name = "Updated Category"
        updated_category.description = "Updated description"
        updated_category.parent_id = None
        updated_category.parent = None
        mock_category_dao.update.return_value = updated_category

        payload = {
            "name": "Updated Category",
            "description": "Updated description",
            "parent_id": None,
        }

        # Act
        response = test_client.put(f"/api/v1/category/{category_id}", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Category"
        mock_category_dao.update.assert_called_once()

    def test_update_category_not_found(self, test_client, mock_category_dao):
        """Test updating non-existent category.

        Args:
            test_client: FastAPI test client fixture.
            mock_category_dao: Mocked CategoryDAO fixture.

        """
        # Arrange
        mock_category_dao.update.side_effect = NoResultFound("Category not found")

        payload = {"name": "Updated Category"}

        # Act
        response = test_client.put("/api/v1/category/999", json=payload)

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_category_parent_not_found(self, test_client, mock_category_dao):
        """Test category update with invalid parent ID.

        Args:
            test_client: FastAPI test client fixture.
            mock_category_dao: Mocked CategoryDAO fixture.

        """
        # Arrange
        mock_category_dao.update.side_effect = IntegrityError("INSERT INTO", None, Exception("Parent not found"))

        payload = {
            "name": "Updated Category",
            "parent_id": 999,
        }

        # Act
        response = test_client.put("/api/v1/category/42", json=payload)

        # Assert
        assert response.status_code == 400
        assert "Related object not found" in response.json()["detail"]

    def test_update_category_db_error(self, test_client, mock_category_dao):
        """Test category update with database error.

        Args:
            test_client: FastAPI test client fixture.
            mock_category_dao: Mocked CategoryDAO fixture.

        """
        # Arrange
        mock_category_dao.update.side_effect = DatabaseError("SELECT *", None, Exception("Database error"))

        payload = {"name": "Updated Category"}

        # Act
        response = test_client.put("/api/v1/category/42", json=payload)

        # Assert
        assert response.status_code == 500
        assert "updating" in response.json()["detail"].lower()


@pytest.mark.api
class TestDeleteCategory:
    """Test DELETE /api/v1/category/{category_id} endpoint."""

    def test_delete_category_success(self, test_client, mock_category_dao):
        """Test successful category deletion.

        Args:
            test_client: FastAPI test client fixture.
            mock_category_dao: Mocked CategoryDAO fixture.

        """
        # Arrange
        category_id = 42
        mock_category_dao.delete.return_value = None

        # Act
        response = test_client.delete(f"/api/v1/category/{category_id}")

        # Assert
        assert response.status_code == 204
        assert response.content == b""
        mock_category_dao.delete.assert_called_once_with(category_id)

    def test_delete_category_not_found(self, test_client, mock_category_dao):
        """Test deleting non-existent category.

        Args:
            test_client: FastAPI test client fixture.
            mock_category_dao: Mocked CategoryDAO fixture.

        """
        # Arrange
        mock_category_dao.delete.side_effect = NoResultFound("Category not found")

        # Act
        response = test_client.delete("/api/v1/category/999")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_category_db_error(self, test_client, mock_category_dao):
        """Test category deletion with database error.

        Args:
            test_client: FastAPI test client fixture.
            mock_category_dao: Mocked CategoryDAO fixture.

        """
        # Arrange
        mock_category_dao.delete.side_effect = DatabaseError("SELECT *", None, Exception("Database error"))

        # Act
        response = test_client.delete("/api/v1/category/42")

        # Assert
        assert response.status_code == 500
        assert "deleting" in response.json()["detail"].lower()


@pytest.mark.api
class TestGetCategoryListFilters:
    """Test GET /api/v1/category with filters query param."""

    def test_get_category_list_with_eq_filter(self, test_client, mock_category_dao):
        """Test that a filter passed via query param reaches get_all.

        Args:
            test_client: FastAPI test client fixture.
            mock_category_dao: Mocked CategoryDAO fixture.

        """
        mock_category_dao.get_all.return_value = ([], 0)
        filters = [{"column": "name", "operator": "eq", "value": "Food"}]

        response = test_client.get("/api/v1/category", params={"filters": json.dumps(filters)})

        assert response.status_code == 200
        call_kwargs = mock_category_dao.get_all.call_args.kwargs
        assert call_kwargs["filters"] is not None
        assert len(call_kwargs["filters"]) == 1
        assert call_kwargs["filters"][0]["column"] == "name"
        assert call_kwargs["filters"][0]["operator"] == "eq"
        assert call_kwargs["filters"][0]["value"] == "Food"

    def test_get_category_list_with_isnull_filter(self, test_client, mock_category_dao):
        """Test that an isnull filter is forwarded to get_all.

        Args:
            test_client: FastAPI test client fixture.
            mock_category_dao: Mocked CategoryDAO fixture.

        """
        mock_category_dao.get_all.return_value = ([], 0)
        filters = [{"column": "parent_id", "operator": "isnull", "value": None}]

        response = test_client.get("/api/v1/category", params={"filters": json.dumps(filters)})

        assert response.status_code == 200
        call_kwargs = mock_category_dao.get_all.call_args.kwargs
        assert call_kwargs["filters"] is not None
        assert call_kwargs["filters"][0]["operator"] == "isnull"

    def test_get_category_list_without_filters_passes_none(self, test_client, mock_category_dao):
        """Test that omitting filters passes None to get_all.

        Args:
            test_client: FastAPI test client fixture.
            mock_category_dao: Mocked CategoryDAO fixture.

        """
        mock_category_dao.get_all.return_value = ([], 0)

        response = test_client.get("/api/v1/category")

        assert response.status_code == 200
        call_kwargs = mock_category_dao.get_all.call_args.kwargs
        assert call_kwargs["filters"] is None
