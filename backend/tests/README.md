# Backend Tests

This directory contains the test suite for the Expenses Counter backend.

## Test Setup

The test configuration is defined in `conftest.py` and provides several fixtures for database testing. **The test database is automatically dropped after all tests complete**, ensuring clean test runs with no leftover data.

### Session-Level Fixtures

#### `test_database_with_migrations`
Creates a temporary SQLite database and generates all tables from SQLAlchemy models. This fixture runs once per test session, providing a fully set up database for all tests. The database file is automatically deleted when the test session ends.

Note: This fixture creates tables directly from SQLAlchemy metadata rather than running Alembic migrations. This approach is simpler and more reliable for testing, as it avoids event loop conflicts and is faster than running migrations.

**Usage:**
```python
async def test_something(test_database_with_migrations):
    # Database is created with all tables
    # Use async_db_client to interact with it
    pass
```

#### `async_db_client`
Provides an `AsyncDatabaseClient` instance connected to the test database. This is a session-scoped fixture that returns a singleton database client. The database connection is properly closed and the database file is dropped after all tests complete.

**Usage:**
```python
@pytest.mark.asyncio
async def test_database_operations(async_db_client):
    async for session in async_db_client.get_session():
        # Perform database operations
        result = await session.execute(select(Category))
        categories = result.scalars().all()
```

### Function-Level Fixtures

#### `db_session`
Provides a database session that automatically rolls back after each test. This ensures test isolation - changes made in one test won't affect other tests.

**Usage:**
```python
@pytest.mark.asyncio
async def test_create_category(db_session):
    category = Category(name="Test")
    db_session.add(category)
    await db_session.commit()
    # Session is automatically rolled back after the test
```

## Running Tests

### Run all tests
```bash
cd backend
uv run pytest
```

### Run tests with coverage
Coverage is enabled by default. Reports are generated automatically:
- **Terminal**: Shows coverage summary with missing lines
- **HTML**: Detailed report in `backend/htmlcov/index.html`

```bash
cd backend
uv run pytest
```

To run tests without coverage:
```bash
cd backend
uv run pytest --no-cov
```

### Run specific test file
```bash
cd backend
uv run pytest tests/test_database.py
```

### Run specific test class or function
```bash
cd backend
uv run pytest tests/test_database.py::TestDatabaseSetup::test_database_client_connection
```

### Run tests with verbose output
```bash
cd backend
uv run pytest -v
```

### Run tests by marker
```bash
cd backend
# Run only API tests
uv run pytest -m api

# Run only non-API tests (database, etc.)
uv run pytest -m "not api"

# Run async tests
uv run pytest -m asyncio

# Run integration tests
uv run pytest -m integration
```

## Writing Tests

### Basic Test Structure

```python
import pytest
from sqlalchemy import select, text

from expenses_counter.services.database import AsyncDatabaseClient
from expenses_counter.services.database.models import YourModel


@pytest.mark.asyncio
class TestYourModel:
    """Test your model operations."""

    async def test_database_connection(self, async_db_client):
        """Test that database is accessible."""
        is_healthy = await async_db_client.healthcheck()
        assert is_healthy

    async def test_create_record(self, db_session):
        """Test creating a record."""
        # Arrange
        record = YourModel(name="Test", description="Test record")

        # Act
        db_session.add(record)
        await db_session.commit()

        # Assert
        result = await db_session.execute(
            select(YourModel).where(YourModel.name == "Test")
        )
        created = result.scalar_one()
        assert created.name == "Test"
```

### Test Isolation and Cleanup

### Transaction Isolation
Tests are isolated using transaction rollback. Each test:
1. Gets a fresh database session
2. Performs operations within a transaction
3. Has the transaction automatically rolled back after completion

This means tests can create, modify, or delete data without affecting other tests.

### Database Cleanup
The test database is automatically dropped after the test session:
1. A temporary SQLite database file is created at the start of the test session
2. All tables are created from SQLAlchemy models
3. Tests run with transaction isolation
4. After all tests complete, the database connection is closed
5. The temporary database file is deleted

No manual cleanup is needed - everything is handled automatically by the fixtures.

### When to Use Each Fixture

- **`db_session`**: Default choice for most tests. Provides transaction rollback for test isolation.
- **`async_db_client`**: When you need direct access to the database client or want to manage sessions manually.

## Test Configuration

Test configuration is defined in `backend/pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "session"
addopts = [
    "-vvv",
    "--strict-markers",
    "--tb=short",
    "--cov=src/expenses_counter",
    "--cov-report=term-missing",
    "--cov-report=html",
]

[tool.coverage.run]
source = ["src/expenses_counter"]
omit = [
    "*/tests/*",
    "*/migrations/*",
    "*/alembic/*",
]
branch = true

[tool.coverage.report]
precision = 2
show_missing = true
```

Key settings:
- `asyncio_mode = "auto"`: Automatically detects and runs async tests
- `asyncio_default_fixture_loop_scope = "session"`: Allows session-scoped async fixtures
- `--cov=src/expenses_counter`: Measures coverage for the source code
- `branch = true`: Includes branch coverage analysis
- Coverage reports exclude tests, migrations, and alembic directories

### Available Test Markers

Tests can be marked with the following pytest markers:

- **`@pytest.mark.api`**: API endpoint tests (using mocked dependencies)
- **`@pytest.mark.asyncio`**: Async tests (automatically applied to async test functions)
- **`@pytest.mark.integration`**: Integration tests (tests that use multiple components)
- **`@pytest.mark.slow`**: Slow-running tests

Use markers to run specific subsets of tests:
```bash
# Run only API tests
uv run pytest -m api

# Run all tests except slow ones
uv run pytest -m "not slow"

# Run integration tests
uv run pytest -m integration
```

## Examples

See `test_database.py` for examples of:
- Testing database connectivity
- Verifying tables were created
- Using the db_session fixture

## Troubleshooting

### "RuntimeError: Event loop is closed"
This usually means you're trying to use an async fixture with the wrong scope. Make sure:
- Session-scoped async fixtures use the `event_loop` fixture
- Function-scoped async fixtures use `@pytest.mark.asyncio`

### "Database is locked"
SQLite can sometimes lock when multiple connections are open. Ensure:
- Tests properly close sessions
- The `db_session` fixture is used correctly
- You're not mixing manual session creation with fixture sessions

### "Table already exists" or migration errors
The test database is created fresh for each test session. If you see these errors:
- Make sure the `test_db_path` is using a temporary directory
- Check that cleanup is running (the fixture should remove the test DB file)
- Manually delete any orphaned test DB files in `/tmp`

## Continuous Integration

Tests are automatically run on every pull request to `master` and `development` branches via GitHub Actions.

### Workflow: `test-backend`

The workflow (`.github/workflows/test_backend.yml`) performs the following:

1. **Sets up Python 3.13** with uv package manager
2. **Installs dependencies** using `uv sync --all-groups`
3. **Runs tests with coverage** using `uv run pytest`
4. **Archives HTML coverage report** as a workflow artifact (available for 7 days)

The workflow only runs when backend files or the workflow file itself are modified, making CI more efficient.

## Best Practices

1. **Use `db_session` by default**: It provides automatic cleanup and test isolation.
2. **Mark async tests**: Always use `@pytest.mark.asyncio` for async test functions.
3. **Test one thing**: Each test should verify a single behavior or outcome.
4. **Clean up properly**: Let fixtures handle cleanup; avoid manual cleanup code.
5. **Use descriptive names**: Test names should clearly describe what they test.
6. **Arrange-Act-Assert**: Structure tests with clear setup, execution, and verification phases.
