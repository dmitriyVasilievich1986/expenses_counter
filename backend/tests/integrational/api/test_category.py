"""Integration tests for category API endpoints.

This module provides integration tests for the category router using FastAPI's
TestClient for real HTTP requests without mocks.

Note: Some advanced features like eager-loaded relationships may not work
perfectly with TestClient due to async session management complexities.
These tests focus on core CRUD operations and API contract validation.
"""

import pytest
from fastapi.testclient import TestClient

from expenses_counter.config import AppConfig
from expenses_counter.modules.app import get_app
from expenses_counter.modules.middlewares.dependencies import user_authorized


@pytest.fixture
def test_app(test_config: AppConfig, test_user_in_db):
    """Create a test FastAPI application with the test user wired into auth.

    Args:
        test_config: Test configuration with database settings.
        test_user_in_db: Real ``User`` row used as the authenticated principal.

    Returns:
        FastAPI: Application instance for testing.

    """
    app = get_app(test_config)
    app.dependency_overrides[user_authorized] = lambda: test_user_in_db
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
def client(test_app, test_database_with_migrations):  # noqa: ARG001
    """Create a test client for the FastAPI application.

    Args:
        test_app: The test FastAPI application.
        test_database_with_migrations: Ensure database is set up.

    Returns:
        TestClient: FastAPI test client for making requests.

    """
    return TestClient(test_app)


@pytest.mark.integration
class TestCategoryIntegration:
    """Integration tests for category endpoints."""

    def test_create_and_get_category(self, client):
        """Test creating a category and retrieving it.

        Args:
            client: FastAPI test client fixture.

        """
        # Create a category via API
        payload = {
            "name": "Food & Drinks",
            "description": "All food and beverage expenses",
        }
        response = client.post("/api/v1/category", json=payload)
        assert response.status_code == 201
        category_id = response.json()["id"]

        # Retrieve the category via API
        response = client.get(f"/api/v1/category/{category_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Food & Drinks"

    def test_create_multiple_categories(self, client):
        """Test creating multiple categories.

        Args:
            client: FastAPI test client fixture.

        """
        categories_data = [
            {"name": "Transport", "description": "Transportation costs"},
            {"name": "Entertainment", "description": "Entertainment expenses"},
            {"name": "Healthcare", "description": "Medical expenses"},
        ]

        created_ids = []
        for cat_data in categories_data:
            response = client.post("/api/v1/category", json=cat_data)
            assert response.status_code == 201
            created_ids.append(response.json()["id"])

        # Verify each category can be retrieved
        for category_id in created_ids:
            response = client.get(f"/api/v1/category/{category_id}")
            assert response.status_code == 200

    def test_get_all_categories(self, client):
        """Test listing all categories with pagination.

        Args:
            client: FastAPI test client fixture.

        """
        # Create some categories first
        for i in range(3):
            payload = {"name": f"Category {i}", "description": f"Description {i}"}
            response = client.post("/api/v1/category", json=payload)
            assert response.status_code == 201

        # Get all categories
        response = client.get("/api/v1/category?limit=100&offset=0")
        assert response.status_code == 200

    def test_update_category(self, client):
        """Test updating a category.

        Args:
            client: FastAPI test client fixture.

        """
        # Create category
        create_payload = {
            "name": "Personal Care",
            "description": "Personal care products",
        }
        create_response = client.post("/api/v1/category", json=create_payload)
        assert create_response.status_code == 201
        category_id = create_response.json()["id"]

        # Update category
        update_payload = {
            "name": "Health & Personal Care",
            "description": "Health and personal care products",
        }
        update_response = client.put(f"/api/v1/category/{category_id}", json=update_payload)
        assert update_response.status_code == 200

        # Verify via GET
        get_response = client.get(f"/api/v1/category/{category_id}")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == "Health & Personal Care"

    def test_delete_category(self, client):
        """Test deleting a category.

        Args:
            client: FastAPI test client fixture.

        """
        # Create category
        create_payload = {"name": "Temporary Category", "description": "To be deleted"}
        create_response = client.post("/api/v1/category", json=create_payload)
        assert create_response.status_code == 201
        category_id = create_response.json()["id"]

        # Verify it exists
        get_response = client.get(f"/api/v1/category/{category_id}")
        assert get_response.status_code == 200

        # Delete category
        delete_response = client.delete(f"/api/v1/category/{category_id}")
        assert delete_response.status_code == 204

        # Verify it's deleted
        get_response = client.get(f"/api/v1/category/{category_id}")
        assert get_response.status_code == 404

    def test_get_nonexistent_category(self, client):
        """Test retrieving a category that doesn't exist.

        Args:
            client: FastAPI test client fixture.

        """
        response = client.get("/api/v1/category/99999")
        assert response.status_code == 404

    def test_update_nonexistent_category(self, client):
        """Test updating a category that doesn't exist.

        Args:
            client: FastAPI test client fixture.

        """
        update_payload = {"name": "Updated Name", "description": "Updated"}
        response = client.put("/api/v1/category/99999", json=update_payload)
        assert response.status_code == 404

    def test_delete_nonexistent_category(self, client):
        """Test deleting a category that doesn't exist.

        Args:
            client: FastAPI test client fixture.

        """
        response = client.delete("/api/v1/category/99999")
        assert response.status_code == 404

    def test_create_category_validation_error(self, client):
        """Test creating a category with invalid data.

        Args:
            client: FastAPI test client fixture.

        """
        # Try to create category with empty name
        payload = {"name": "", "description": "Empty name should fail"}
        response = client.post("/api/v1/category", json=payload)
        assert response.status_code == 422  # Validation error

    def test_pagination(self, client):
        """Test pagination functionality.

        Args:
            client: FastAPI test client fixture.

        """
        # Test pagination parameters are accepted
        response = client.get("/api/v1/category?limit=2&offset=0")
        assert response.status_code == 200

        # Test second page
        response = client.get("/api/v1/category?limit=2&offset=2")
        assert response.status_code == 200

    def test_create_category_with_parent_basic(self, client):
        """Test creating a category with a parent.

        Args:
            client: FastAPI test client fixture.

        """
        # Create parent category
        parent_response = client.post("/api/v1/category", json={"name": "Parent", "description": "Parent category"})
        assert parent_response.status_code == 201
        parent_id = parent_response.json()["id"]

        # Create child category
        child_response = client.post(
            "/api/v1/category",
            json={
                "name": "Child",
                "description": "Child category",
                "parent_id": parent_id,
            },
        )
        assert child_response.status_code == 201

    def test_get_root_categories_endpoint(self, client):
        """Test the root categories endpoint.

        Args:
            client: FastAPI test client fixture.

        """
        response = client.get("/api/v1/category/parent")
        assert response.status_code == 200

    def test_get_categories_by_parent_endpoint(self, client):
        """Test the get categories by parent endpoint.

        Args:
            client: FastAPI test client fixture.

        """
        # Create a parent first
        parent_response = client.post("/api/v1/category", json={"name": "TestParent", "description": "Test"})
        assert parent_response.status_code == 201
        parent_id = parent_response.json()["id"]

        # Query children
        response = client.get(f"/api/v1/category/parent/{parent_id}")
        assert response.status_code == 200
