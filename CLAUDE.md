# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Expenses Counter is a full-stack expense tracking application with a Python/FastAPI backend and React frontend. The application tracks personal expenses by organizing them into products, categories, shops, and addresses, providing structured analysis of spending patterns.

**Tech Stack:**

- Backend: Python 3.13, FastAPI, SQLAlchemy 2.0 (async), PostgreSQL/SQLite
- Frontend: React 18, Redux Toolkit, Material-UI, TypeScript/JavaScript
- Build Tools: uv (Python), webpack (JavaScript)
- Database Migrations: Alembic
- Linting/Formatting: Ruff (Python)

## Development Commands

### Backend

The backend uses **uv** for package management. All backend commands should be run from the `backend/` directory.

```bash
# Install dependencies and create virtual environment
uv sync

# Activate virtual environment
source .venv/bin/activate  # Unix/macOS
.venv\Scripts\activate     # Windows

# Run the application
uv run expenses_counter run                    # Production mode
uv run expenses_counter run --reload           # Development mode with auto-reload
uv run expenses_counter run --host 0.0.0.0 --port 8000  # Custom host/port

# Show configuration
uv run expenses_counter show-config

# Database migrations
uv run alembic revision --autogenerate -m "description"  # Generate migration
uv run alembic upgrade head                              # Apply migrations
uv run alembic downgrade -1                              # Rollback one migration
uv run alembic history                                   # View migration history

# Code quality
uv run ruff check src/          # Lint code
uv run ruff check --fix src/    # Auto-fix linting issues
uv run ruff format src/         # Format code
uv run ruff format --check src/ # Check formatting without changes

# Build package
python -m pip install build
python -m build
```

### Frontend

All frontend commands should be run from the `frontend/` directory.

```bash
# Install dependencies
npm ci  # Recommended for CI/CD
npm install

# Development build (watches for changes, outputs to ../backend/static/js)
npm run dev

# Production build (outputs to ../backend/static/js)
npm run build
```

**Important:** The frontend build outputs directly to `../backend/static/js`, where the backend serves static files. This is configured in webpack and package.json scripts.

## Architecture

### Backend Architecture

The backend follows a layered architecture with clear separation of concerns:

```
backend/src/expenses_counter/
├── config/              # Configuration management (YAML-based with Pydantic)
│   ├── models/          # Config data models (API, CORS, Database settings)
│   ├── base/            # Base configuration classes and storage
│   └── app_config.py    # Main AppConfig singleton
├── modules/             # FastAPI application layer
│   ├── app.py           # Application factory (get_app)
│   ├── routers/         # API endpoints (system/, api/)
│   └── middlewares/     # App lifecycle and dependencies
├── services/            # Core business logic
│   ├── database/        # Database client and SQLAlchemy models
│   ├── daos/            # Data Access Objects (CRUD operations)
│   └── alembic/         # Database migrations
└── utils/               # Utility functions
    ├── cli/             # Click CLI commands
    ├── singleton.py     # Singleton pattern implementation
    └── versioning/      # Version management utilities
```

**Key Architectural Patterns:**

1. **Application Factory**: `expenses_counter.modules.app:get_app` creates the FastAPI app with configuration injection
2. **Singleton Pattern**: `DatabaseClient` and `AppConfig` use singleton pattern to ensure single instances
3. **DAO Pattern**: Each entity (Category, Shop, Address, Product, Transaction) has a DAO for data access
4. **Generic Base DAO**: `BaseDAO` provides type-safe CRUD operations with generic type parameters (B, T, C, U, M)
5. **Async Throughout**: All database operations use async/await for non-blocking I/O

**Database Models & Relationships:**

```
Category (hierarchical, self-referential)
    ├── parent_id → Category
    ├── shops → Shop[]
    └── products → Product[] (as subcategory)

Shop
    ├── category_id → Category
    └── addresses → Address[]

Address
    ├── shop_id → Shop
    └── transactions → Transaction[]

Product
    ├── sub_category_id → Category
    └── transactions → Transaction[]

Transaction
    ├── product_id → Product
    └── address_id → Address
```

**DAO Schema Pattern:**

Each DAO includes Pydantic schemas for different operations:

- **Get**: Full response schema with all fields and relationships
- **Post**: Creation schema with required fields only
- **Put**: Full update requiring all fields
- **Patch**: Partial update with all optional fields

**API Endpoints:**

All entity endpoints follow RESTful conventions:

- `GET /api/v1/{entity}/` - List all
- `GET /api/v1/{entity}/{id}` - Get by ID
- `POST /api/v1/{entity}/` - Create
- `PUT /api/v1/{entity}/{id}` - Full update
- `PATCH /api/v1/{entity}/{id}` - Partial update
- `DELETE /api/v1/{entity}/{id}` - Delete

System endpoints:

- `GET /health` - Health check (tests database connection)
- `GET /version` - Application version

### Frontend Architecture

The frontend is a React SPA built with Redux for state management:

```
frontend/src/
├── components/
│   ├── App.tsx          # Main app component
│   ├── api/             # API client and requests
│   ├── assets/          # Static assets (images, icons)
│   ├── components/      # Reusable UI components
│   ├── pages/           # Page-level components
│   ├── reducers/        # Redux reducers
│   ├── Select/          # Custom select components
│   └── support/         # Helper functions
├── styles/              # SASS/SCSS stylesheets
└── index.js             # Entry point
```

**Build Configuration:**

- Webpack bundles to `main.js` output in `../backend/static/js`
- CSS Modules enabled with `[folder]__[local]` naming
- TypeScript and JSX/TSX support via ts-loader and babel-loader
- SASS/SCSS support with style-loader, css-loader, sass-loader
- Path aliases: `Assets`, `Reducers`, `Constants`

### Configuration System

The backend uses a sophisticated YAML-based configuration system:

- Configuration is managed by `AppConfig` singleton (`config/app_config.py`)
- Loads from YAML files in `backend/configurations/`
- Supports environment variable overrides
- Main sections: API info, CORS settings, Database connection
- Accessed via `AppConfig.get_or_create()` throughout the app

### Version Management

Version is stored in `backend/src/expenses_counter/__init__.py`:

```python
__version__ = "X.Y.Z"
```

Version bumping is handled by `.github/scripts/bump_version.py`:

- Development branch: bumps PATCH version
- Master branch: bumps MINOR version and resets PATCH to 0

## CI/CD

GitHub Actions workflows in `.github/workflows/`:

**build_backend.yml:**

- Runs on push/PR to master or development
- Lints with `ruff check src/`
- Checks formatting with `ruff format --check src/`
- Builds package with `python -m build`

**build_frontend.yml:**

- Runs on push/PR to master or development
- Installs dependencies with `npm ci`
- Builds with `npm run build`
- Uploads artifacts to `frontend/dist/`

## Code Style

**Python (Backend):**

- Ruff configuration in `backend/pyproject.toml`
- Line length: 120 characters
- Extensive rule set enabled (see pyproject.toml for details)
- Import order: future → standard-library → third-party → first-party → local-folder
- Docstrings required for modules, classes, and public methods

**JavaScript/TypeScript (Frontend):**

- Babel configuration in `frontend/.babelrc`
- TypeScript configuration in `frontend/tsconfig.json`
- Webpack configuration in `frontend/webpack.config.js`

## Database

The application supports both PostgreSQL (production) and SQLite (development/testing):

- Connection configured via `AppConfig.services.database.url`
- Uses async drivers: `asyncpg` for PostgreSQL, `aiosqlite` for SQLite
- All models inherit from SQLAlchemy declarative base
- Relationships use lazy loading with `selectinload` for eager loading when needed

**Migration Workflow:**

1. Modify models in `services/database/models/`
2. Generate migration: `uv run alembic revision --autogenerate -m "description"`
3. Review generated migration in `services/alembic/versions/`
4. Apply migration: `uv run alembic upgrade head`

## Entry Points

**Backend:**

- CLI: `expenses_counter` command (defined in `pyproject.toml` project.scripts)
- Module: `python -m expenses_counter` (via `__main__.py`)
- Factory: `expenses_counter.modules.app:get_app` (for Uvicorn)

**Frontend:**

- Entry: `frontend/src/index.js`
- Output: `backend/static/js/main.js`

## Testing

Test configuration is present in `backend/pyproject.toml`:

```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "expense_counter.expense_counter.tests_settings"
```

Note: The test settings reference suggests Django was previously used or tests are being migrated.
