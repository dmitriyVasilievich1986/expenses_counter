# Expenses Counter Backend

A Python-based expense tracking application built with FastAPI and SQLAlchemy. This application provides a RESTful API for managing personal expenses, transactions, shops, products, and categories.

## Overview

Expenses Counter is designed to help track and analyze personal expenses by organizing them into products, categories, shops, and specific shop addresses. It provides a structured way to record transactions and understand spending patterns across different stores and product categories.

## Features

- **Transaction Management**: Track individual purchases with date, quantity, and price
- **Product Catalog**: Organize products with descriptions and subcategories
- **Shop Management**: Maintain information about shops including multiple locations
- **Category System**: Hierarchical category structure for organizing shops and products
- **Address Tracking**: Support multiple addresses for each shop
- **RESTful API**: Full CRUD operations for all entities
- **Async Support**: Built on asyncio for high-performance database operations
- **Database Migrations**: Version-controlled schema changes with Alembic

## Tech Stack

- **Python 3.13+**: Modern Python features and performance improvements
- **FastAPI**: High-performance async web framework
- **SQLAlchemy 2.0**: Async ORM with declarative models
- **Alembic**: Database migration management
- **Pydantic**: Data validation and serialization
- **PostgreSQL/SQLite**: Flexible database support via asyncpg/aiosqlite
- **Uvicorn**: ASGI server for production deployment
- **Loguru**: Advanced logging capabilities

## Package Management

This project uses **[uv](https://github.com/astral-sh/uv)** for package and virtual environment management. uv is a fast Python package installer and resolver written in Rust.

### Installation

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync

# Activate the virtual environment
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

### Running the Application

```bash
# Run the application
uv run expenses_counter

# Or activate the venv and run directly
source .venv/bin/activate
expenses_counter
```

## Project Structure

```
backend/
├── src/
│   └── expenses_counter/
│       ├── config/              # Configuration management
│       ├── modules/             # FastAPI application and routers
│       │   ├── routers/         # API endpoints
│       │   └── middlewares/     # App lifecycle and dependencies
│       ├── services/            # Core business logic
│       │   ├── alembic/         # Database migrations
│       │   ├── daos/            # Data Access Objects
│       │   └── database/        # Database client and models
│       └── utils/               # Utility functions
├── pyproject.toml               # Project metadata and dependencies
└── README.md                    # This file
```

## Services Overview

The `backend/src/expenses_counter/services` folder contains the core business logic and data access layers of the application.

### 1. Database Service (`database/`)

**Purpose**: Manages database connections and defines data models.

**Components**:
- **DatabaseClient** (`client.py`): Singleton async database client that manages SQLAlchemy engine and session factory
  - Provides session management for database operations
  - Includes health check functionality
  - Supports both PostgreSQL (via asyncpg) and SQLite (via aiosqlite)

**Models** (`models/`):
- **Base**: SQLAlchemy declarative base for all models
- **Shop**: Represents retail stores/vendors with optional categories and icons
- **Address**: Physical locations of shops (one shop can have multiple addresses)
- **Category**: Hierarchical category system with parent-child relationships
- **Product**: Items that can be purchased, linked to subcategories
- **Transaction**: Individual purchase records with date, quantity, price, linked to products and addresses

### 2. Data Access Objects Service (`daos/`)

**Purpose**: Provides abstraction layer between API and database, implementing CRUD operations for each entity.

**Base DAO** (`base/base_dao.py`):
- Abstract base class defining standard CRUD interface
- Generic type parameters for type safety (B, T, C, U, M)
- Methods: `get_by_id`, `get_all`, `create`, `update`, `modify`, `delete`

**Entity-Specific DAOs**:

#### AddressDAO (`daos/address/`)
- Manages shop addresses (physical locations)
- Validates shop existence before creating/updating
- Eager loads related shop data
- **Operations**: Create addresses for shops, update location details, retrieve addresses with shop information

#### CategoryDAO (`daos/category/`)
- Manages hierarchical categories with parent-child relationships
- Supports self-referential relationships for nested categories
- Validates parent category existence
- **Operations**: Create category hierarchies, organize shops and products, update category information

#### ProductDAO (`daos/product/`)
- Manages product catalog
- Links products to subcategories
- Validates subcategory existence
- **Operations**: Add products to catalog, categorize items, update product details

#### ShopDAO (`daos/shop/`)
- Manages shop information and metadata
- Associates shops with categories
- Supports optional icons for visual identification
- **Operations**: Register shops, categorize stores, update shop details

#### TransactionDAO (`daos/transaction/`)
- Manages purchase transactions
- Links transactions to products and addresses
- Validates product and address existence
- Records date, quantity, and price information
- **Operations**: Record purchases, track expenses, update transaction details

**Schema Organization**:
Each DAO includes Pydantic schemas for:
- **Get**: Response schema with all fields including relationships
- **Post**: Creation schema with required fields
- **Put**: Full update schema requiring all fields
- **Patch**: Partial update schema with optional fields

### 3. Alembic Migrations Service (`alembic/`)

**Purpose**: Manages database schema versioning and migrations.

**Key Files**:
- **env.py**: Alembic environment configuration for async migrations
- **versions/**: Migration history with timestamped revision files

**Migration History** (chronological):
1. Initial database setup
2. Base tables creation (shop, category, product)
3. Transaction and shop address tables
4. Price type adjustments
5. Category hierarchy implementation
6. Field additions and modifications

## Data Model Relationships

```
Category (hierarchical)
    ├── parent_id → Category (self-referential)
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

## Usage Examples

### Using the DatabaseClient

```python
from expenses_counter.services.database import DatabaseClient
from expenses_counter.config import AppConfig

# Initialize the database client
config = AppConfig()
db_client = DatabaseClient(config)

# Get a session and perform queries
async for session in db_client.get_session():
    from sqlalchemy import select
    from expenses_counter.services.database.models import Category

    result = await session.execute(
        select(Category).where(Category.name == "Groceries")
    )
    category = result.scalar_one_or_none()
```

### Using DAOs

```python
from expenses_counter.services.database import DatabaseClient
from expenses_counter.services.daos.category import CategoryDAO
from expenses_counter.services.daos.category.schemas import CategoryPost
from expenses_counter.config import AppConfig

# Initialize
config = AppConfig()
db_client = DatabaseClient(config)
category_dao = CategoryDAO(db_client)

# Create a new category
new_category = await category_dao.create(
    CategoryPost(
        name="Electronics",
        description="Electronic devices and accessories",
        parent_id=None
    )
)

# Get all categories
categories = await category_dao.get_all()

# Get category by ID
category = await category_dao.get_by_id(1)

# Update category (full update)
from expenses_counter.services.daos.category.schemas import CategoryPut
updated = await category_dao.update(
    1,
    CategoryPut(
        name="Consumer Electronics",
        description="Updated description",
        parent_id=None
    )
)

# Partial update
from expenses_counter.services.daos.category.schemas import CategoryPatch
modified = await category_dao.modify(
    1,
    CategoryPatch(name="Electronics & Gadgets")
)

# Delete category
success = await category_dao.delete(1)
```

### Creating a Complete Transaction

```python
from expenses_counter.services.daos.shop import ShopDAO
from expenses_counter.services.daos.address import AddressDAO
from expenses_counter.services.daos.category import CategoryDAO
from expenses_counter.services.daos.product import ProductDAO
from expenses_counter.services.daos.transaction import TransactionDAO
from datetime import date

# Initialize DAOs
shop_dao = ShopDAO(db_client)
address_dao = AddressDAO(db_client)
category_dao = CategoryDAO(db_client)
product_dao = ProductDAO(db_client)
transaction_dao = TransactionDAO(db_client)

# 1. Create a category
category = await category_dao.create(
    CategoryPost(name="Food", description="Food items", parent_id=None)
)

# 2. Create a shop
from expenses_counter.services.daos.shop.schemas import ShopPost
shop = await shop_dao.create(
    ShopPost(
        name="Local Grocery Store",
        description="Neighborhood grocery",
        category_id=category.id,
        icon="🛒"
    )
)

# 3. Create an address for the shop
from expenses_counter.services.daos.address.schemas import AddressPost
address = await address_dao.create(
    AddressPost(
        local_name="Downtown Location",
        address="123 Main St, City",
        shop_id=shop.id
    )
)

# 4. Create a product
from expenses_counter.services.daos.product.schemas import ProductPost
product = await product_dao.create(
    ProductPost(
        name="Organic Apples",
        description="Fresh organic apples",
        sub_category_id=category.id
    )
)

# 5. Create a transaction
from expenses_counter.services.daos.transaction.schemas import TransactionPost
transaction = await transaction_dao.create(
    TransactionPost(
        date=date.today(),
        count=2.5,  # 2.5 kg
        price=12.50,
        product_id=product.id,
        address_id=address.id
    )
)

print(f"Transaction created: {transaction.id}")
print(f"Purchased {transaction.count} of {product.name}")
print(f"Total: ${transaction.price} at {shop.name}")
```

### Querying with Relationships

```python
from expenses_counter.services.daos.transaction import TransactionDAO

transaction_dao = TransactionDAO(db_client)

# Get transaction with all related data
transaction = await transaction_dao.get_by_id(1)

# The transaction object includes:
# - transaction.product (Product details with subcategory)
# - transaction.address (Address details with shop information)

print(f"Product: {transaction.product.name}")
print(f"Shop: {transaction.address.shop.name}")
print(f"Location: {transaction.address.address}")
```

## API Endpoints

The application exposes RESTful API endpoints for all entities:

- **Categories**: `/api/v1/category/`
- **Shops**: `/api/v1/shop/`
- **Addresses**: `/api/v1/address/`
- **Products**: `/api/v1/product/`
- **Transactions**: `/api/v1/transaction/` (to be implemented)

Each endpoint supports:
- `GET /` - List all entities
- `GET /{id}` - Get entity by ID
- `POST /` - Create new entity
- `PUT /{id}` - Full update of entity
- `PATCH /{id}` - Partial update of entity
- `DELETE /{id}` - Delete entity

System endpoints:
- `GET /health` - Health check
- `GET /version` - Application version

## Database Migrations

### Creating a New Migration

```bash
# Generate a new migration
uv run alembic revision --autogenerate -m "description of changes"

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1

# View migration history
uv run alembic history
```

## Development

### Running with Development Server

```bash
# Run with auto-reload
uv run uvicorn expenses_counter.modules.app:app --reload --host 0.0.0.0 --port 8000
```

### Code Quality

The project uses Ruff for linting and formatting:

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Fix linting issues
uv run ruff check --fix .
```

## Configuration

The application uses YAML configuration files. Configuration can be customized via:

- Environment variables
- YAML configuration files
- Pydantic settings

Key configuration sections:
- **API Info**: Debug mode, host, port settings
- **CORS**: Cross-origin resource sharing settings
- **Database**: Connection URL and options

## Architecture Highlights

### Singleton Pattern
The DatabaseClient uses the Singleton pattern to ensure a single database connection pool across the application.

### Async Throughout
All database operations use async/await for non-blocking I/O, enabling high concurrency.

### Type Safety
Extensive use of Python type hints and Pydantic models ensures type safety and better IDE support.

### Separation of Concerns
- **Models**: Define database schema
- **DAOs**: Handle data access logic
- **Schemas**: Define API contracts
- **Routers**: Handle HTTP requests/responses

### Generic Base DAO
The BaseDAO uses generic type parameters to provide type-safe CRUD operations while reducing code duplication.

## License

MIT License - See LICENSE file for details.

## Contributing

This is a personal project, but suggestions and feedback are welcome!
