"""Database setup and connectivity tests.

This module provides tests for database setup and connectivity,
verifying that the test fixtures are working correctly.
"""

import pytest
from sqlalchemy import text

from expenses_counter.services.database import AsyncDatabaseClient


@pytest.mark.asyncio
class TestDatabaseSetup:
    """Test database setup and fixtures."""

    async def test_database_client_connection(self, async_db_client: AsyncDatabaseClient):
        """Test that the database client can connect successfully.

        Args:
            async_db_client: The test database client fixture.

        """
        # Verify health check passes
        is_healthy = await async_db_client.healthcheck()
        assert is_healthy, "Database health check should pass"

    async def test_database_tables_exist(self, async_db_client: AsyncDatabaseClient):
        """Test that all tables were created from SQLAlchemy models.

        Args:
            async_db_client: The test database client fixture.

        """
        async for session in async_db_client.get_session():
            # Query SQLite master table to check table existence
            result = await session.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"))
            tables = [row[0] for row in result.fetchall()]

            # Check that expected tables exist (with main_ prefix)
            expected_tables = [
                "main_category",
                "main_shop",
                "main_shopaddress",
                "main_product",
                "main_transaction",
            ]

            for table in expected_tables:
                assert table in tables, f"Table '{table}' should exist in database"

    async def test_db_session_fixture(self, db_session):
        """Test the db_session fixture for transactional testing.

        This demonstrates that the db_session fixture provides a working
        database session that can execute queries.

        Args:
            db_session: The test database session fixture.

        """
        # Execute a simple query to verify session works
        result = await db_session.execute(text("SELECT 1 as value"))
        row = result.fetchone()

        assert row is not None
        assert row[0] == 1
