# Expenses Counter Backend

A Python 3.13 / FastAPI / SQLAlchemy 2.0 service that tracks personal expenses. It stores transactions tied to products, shops, addresses, and a hierarchical category tree; serves them through a versioned REST API behind JWT auth; and includes a Selenium-based receipt crawler that turns receipt URLs directly into transactions.

## Overview

Expenses Counter organises spending into:

- **Users** — authenticated owners of transactions.
- **Categories** — a self-referential tree used to classify shops and products.
- **Shops** with one or more **Addresses** (physical locations).
- **Products** linked to a category.
- **Transactions** — individual receipt lines linking a user, product, address, date, quantity, and price.

The backend exposes CRUD endpoints for every entity, a statistics endpoint for spending analysis, a JWT-based login flow, and a CLI for running the server, managing the database, managing users, and crawling receipts.

## Features

- **Authentication**: JWT bearer tokens with bcrypt password hashing; per-endpoint `user_authorized` / `admin_required` dependencies.
- **Transaction management**: per-user purchase lines with date, quantity, and price (decimal-precise).
- **Hierarchical categories**: arbitrary-depth `parent` chain eager-loaded by `CategoryDAO`.
- **Receipt crawling**: Selenium + BeautifulSoup pipeline that renders a receipt URL, extracts metadata + line items, and (optionally) persists them as transactions.
- **Statistics**: monthly spend and most-popular-products endpoints.
- **RESTful API** under `/api/v1/` with filtering, pagination, and partial/full update variants.
- **Async everywhere**: `asyncio` + `asyncpg` / `aiosqlite` for non-blocking I/O.
- **Alembic migrations** with both `migrate-db` / `downgrade-db` CLI wrappers.
- **Static asset hosting**: serves the frontend bundle from `backend/static/`.

## Tech Stack

- **Runtime**: Python 3.13+
- **Web**: FastAPI, Uvicorn
- **ORM / DB**: SQLAlchemy 2.0 (async), Alembic, asyncpg + psycopg (PostgreSQL), aiosqlite (SQLite), greenlet
- **Config & validation**: Pydantic v2, pydantic-settings (YAML)
- **Auth**: PyJWT, bcrypt
- **Crawler**: Selenium, webdriver-manager, BeautifulSoup4, lxml
- **CLI**: asyncclick
- **Logging**: Loguru
- **Dev tools**: pytest + pytest-asyncio + pytest-cov, mypy (with SQLAlchemy plugin), Ruff, httpx, pandas (dev-only), ipykernel

## Package Management

The project uses **[uv](https://github.com/astral-sh/uv)** for environments and dependencies.

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync the environment from pyproject.toml / uv.lock
uv sync

# Activate the venv (optional — `uv run` works without activation)
source .venv/bin/activate      # Unix/macOS
.venv\Scripts\activate         # Windows
```

## Running the Application

The package installs a single `expenses_counter` console script (defined in `[project.scripts]`) that exposes every subcommand below. All commands accept `--help`.

```bash
# Start the server (Uvicorn)
uv run expenses_counter run                                 # 0.0.0.0:8000
uv run expenses_counter run --reload                        # dev mode, auto-reload
uv run expenses_counter run --host 127.0.0.1 --port 9000    # custom bind

# Dump the resolved configuration as JSON
uv run expenses_counter show-config
```

### User management

```bash
uv run expenses_counter user create-user --username alice --email alice@example.com
uv run expenses_counter user check-password --username alice
uv run expenses_counter user generate-jwt-token --username alice
uv run expenses_counter user re-generate-password --username alice
```

### Database

```bash
uv run expenses_counter db migrate-db                       # upgrade to head
uv run expenses_counter db migrate-db --revision <rev>      # upgrade to specific revision
uv run expenses_counter db downgrade-db --revision <rev>    # downgrade
uv run expenses_counter db fill-db                          # seed sample data
```

Raw Alembic also works:

```bash
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head
uv run alembic downgrade -1
uv run alembic history
```

### Receipt crawler

```bash
uv run expenses_counter crawler crawl-url --url <receipt-url>
uv run expenses_counter crawler crawl-and-create --url <receipt-url> --username alice
```

`crawl-and-create` runs the headless-Chrome crawler, validates the parsed result, and persists the receipt as transactions owned by the named user. See `src/expenses_counter/utils/web_crawler/README.md` and `src/expenses_counter/commands/crawl_url/README.md` for the crawler internals.

## Project Structure

```
backend/
├── configurations/                  # local.yaml / prod.yaml loaded by AppConfig
├── notebooks/                       # Exploratory notebooks (app_config, auth, daos, web_crawler)
├── src/
│   └── expenses_counter/
│       ├── __init__.py              # __version__
│       ├── __main__.py              # python -m expenses_counter entrypoint
│       ├── commands/                # Reusable command objects (fill_db, crawl_url)
│       ├── config/                  # AppConfig + Pydantic config models
│       │   └── models/
│       │       ├── info/            # api / cors / paths
│       │       └── services/        # auth / database
│       ├── modules/                 # FastAPI app
│       │   ├── app.py               # get_app() factory
│       │   ├── middlewares/         # lifespan + DI dependencies (auth, daos, db)
│       │   └── routers/
│       │       ├── api/v1/          # address, category, product, shop, transaction,
│       │       │                    # statistics, user
│       │       ├── system/          # health, version, login, index
│       │       └── schemas/         # requests/ + responses/ Pydantic models
│       ├── services/                # Business logic
│       │   ├── alembic/             # env.py + versions/
│       │   ├── auth/                # JWTTokenService, PasswordService
│       │   ├── daos/                # Address/Category/Product/Shop/Transaction/User
│       │   └── database/            # AsyncDatabaseClient + ORM models
│       └── utils/                   # filter, mount_static_files, singleton,
│                                    # cli/, web_crawler/
├── static/                          # Frontend bundle (served by FastAPI)
├── tests/                           # pytest suite (see tests/README.md)
├── pyproject.toml
├── .env / db.env                    # Local environment overrides (gitignored)
└── README.md                        # This file
```

## Services Overview

The `services/` package contains the core business logic.

### `services/database/`

- **`AsyncDatabaseClient`** (`async_client.py`) — Singleton that owns the SQLAlchemy async engine and `async_sessionmaker`. Toggles `PRAGMA foreign_keys=ON` for SQLite, exposes `engine`, `session_factory`, `get_session()`, `close()`, and `healthcheck()`.
- **`models/`** — Declarative SQLAlchemy models:
  - `Base` (declarative base)
  - `User` (`main_user`) — username, email, hashed password, profile fields, `is_admin`, `is_active`, `transactions` relationship
  - `Category` (`main_category`) — self-referential `parent_id`, plus `shops` and `products`
  - `Shop` (`main_shop`) — optional `category_id`, optional icon, `addresses`
  - `Address` (`main_shopaddress`) — `shop_id`, location fields, `transactions`
  - `Product` (`main_product`) — `sub_category_id`, `transactions`
  - `Transaction` (`main_transaction`) — `date`, `count` (Numeric 10,3), `price` (Numeric 10,2), foreign keys to `product`, `address`, and `user`

### `services/auth/`

- **`PasswordService`** — bcrypt password hashing/verification (static methods).
- **`JWTTokenService`** — HS256/HS384/HS512 JWT issuance and decoding with `user_id` + `exp` claims.
- **Models**: `AccessToken`, `JWTTokenMetadata`.

See `src/expenses_counter/services/auth/README.md` for usage examples.

### `services/daos/`

`BaseDAO[DatabaseModel: Base]` (`base/base_dao.py`) is a single-generic-parameter abstract async DAO providing `get_by_pk`, `get_all`, total counting, `create`, `update`, `delete`, filter merging via `base_filters` + `concat_filters`, optional `selectinload` options, and column projection. A DAO can be constructed with either a long-lived `AsyncDatabaseClient` (it opens short-lived sessions) or an injected `AsyncSession`.

Entity DAOs (`expenses_counter.services.daos`):

| DAO | Notes |
| --- | --- |
| `AddressDAO` | Validates shop existence; eager-loads shop. |
| `CategoryDAO` | Loads full ancestor chain via recursive `selectinload(Category.parent)`. |
| `ProductDAO` | Validates sub-category existence. |
| `ShopDAO` | Optional category + icon. |
| `TransactionDAO` | Validates product, address, and user references. |
| `UserDAO` | `get_by_username`; `create()` hashes the plaintext password before insert. |

Pydantic request/response schemas live under `modules/routers/schemas/` (`Get`, `Post`, `Put`, `Patch` variants for each entity).

### `services/alembic/`

Alembic environment (`env.py`) plus timestamped revision files under `versions/`. Use the `expenses_counter db ...` CLI commands above, or invoke `alembic` directly.

## Data Model Relationships

```
User
    └── transactions → Transaction[]

Category (self-referential)
    ├── parent_id → Category
    ├── shops → Shop[]
    └── products → Product[]   (as sub-category)

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
    ├── user_id → User
    ├── product_id → Product
    └── address_id → Address
```

## API

All non-system endpoints are mounted under `/api/v1/` and require a `Authorization: Bearer <jwt>` header (the `user_authorized` dependency). Some destructive routes additionally require `admin_required`.

### Entity endpoints

For each of `address`, `category`, `product`, `shop`, `transaction`, `user`:

| Method | Path | Notes |
| --- | --- | --- |
| `GET`    | `/api/v1/{entity}` | List, with filters / pagination |
| `GET`    | `/api/v1/{entity}/{id}` | Single resource |
| `POST`   | `/api/v1/{entity}` | Create |
| `PUT`    | `/api/v1/{entity}/{id}` | Full update |
| `PATCH`  | `/api/v1/{entity}/{id}` | Partial update |
| `DELETE` | `/api/v1/{entity}/{id}` | Delete (admin-only on most entities) |

Notable extras:

- `GET /api/v1/category/by-shop/{shop_id}` — categories scoped to a shop.
- `GET /api/v1/address/name/{local_name}` — address lookup by local name.
- `GET /api/v1/user/me` — current authenticated user (from JWT).

### Statistics

- `GET /api/v1/statistics/monthly-spend` — total spend per month for the authenticated user, with optional date-range filters.
- `GET /api/v1/statistics/most-popular-products` — top-purchased products.

### System endpoints

- `POST /api/login` — exchange `{username, password}` for `{access_token, expires_at}`.
- `GET /api/health` — checks the database connection.
- `GET /api/version` — current package version.
- `GET /api/` — index.

Interactive OpenAPI docs: `http://localhost:8000/docs`.

## Configuration

The `AppConfig` singleton (`expenses_counter.config.AppConfig`) is built by `pydantic-settings` from a YAML file plus environment variables. The YAML file is selected via the `CONFIG_FILE_PATH` environment variable; `backend/configurations/` holds `local.yaml` and `prod.yaml`.

Config sections:

- **`info.api_info`** (`config/models/info/api.py`) — title, description, debug flag, log level.
- **`info.cors_info`** (`info/cors.py`) — allowed origins / methods / headers / credentials.
- **`info.paths_info`** (`info/paths.py`) — `alembic_ini`, static-files path.
- **`services.database`** (`services/database.py`) — provider (`postgresql+asyncpg` or `sqlite+aiosqlite`), host, port, name, user, password; exposes a `url` property used by `AsyncDatabaseClient`.
- **`services.auth`** (`services/auth.py`) — `jwt_secret_key` (`SecretStr`), `password_secret_key` (`SecretStr`), `jwt_algorithm` (`HS256` | `HS384` | `HS512`).

Environment overrides use nested-key syntax (`SECTION__SUBSECTION__FIELD`). The repo ships two example env files:

- `.env` — application secrets (`CONFIG_FILE_PATH`, `SERVICES__AUTH__JWT_SECRET_KEY`, `SERVICES__AUTH__PASSWORD_SECRET_KEY`, `SERVICES__AUTH__JWT_ALGORITHM`).
- `db.env` — database connection (`SERVICES__DATABASE__HOST` / `PORT` / `NAME` / `USER` / `PASSWORD` / `PROVIDER`).

## Usage Examples

### Issuing a token, then calling an endpoint

```bash
# Create a user (one-time)
uv run expenses_counter user create-user --username alice --email alice@example.com

# Log in via the API
curl -s -X POST http://localhost:8000/api/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"<plaintext>"}'
# → {"access_token":"<jwt>","expires_at":"..."}

# Call a protected endpoint
curl -s http://localhost:8000/api/v1/transaction \
  -H "Authorization: Bearer <jwt>"
```

### Using a DAO directly

```python
from expenses_counter.config import AppConfig
from expenses_counter.services.daos import CategoryDAO
from expenses_counter.services.database import AsyncDatabaseClient

config = AppConfig.get_or_create()
db = AsyncDatabaseClient(app_config=config)

dao = CategoryDAO(database_client=db)

new_category = await dao.create(name="Electronics", description="Gadgets", parent_id=None)
all_categories = await dao.get_all()
one = await dao.get_by_pk(new_category.id)        # parent chain is eager-loaded
await dao.update(pk=new_category.id, name="Consumer Electronics")
await dao.delete(pk=new_category.id)
```

A DAO can also reuse an injected session (e.g. when wiring several DAOs into one transaction):

```python
async with db.session_factory() as session:
    category_dao = CategoryDAO(session=session)
    product_dao = ProductDAO(session=session)
    ...
    await session.commit()
```

### Crawling a receipt into transactions

```bash
uv run expenses_counter crawler crawl-and-create \
  --url 'https://example-receipt-host/receipt/12345' \
  --username alice
```

This loads the receipt with headless Chrome, parses metadata and line items, validates the data, and creates the corresponding `Transaction` rows owned by `alice`. See `src/expenses_counter/commands/crawl_url/README.md` for the persistence command.

## Development

### Code quality

```bash
uv run ruff check src/             # Lint
uv run ruff check --fix src/       # Auto-fix
uv run ruff format src/            # Format
uv run ruff format --check src/    # CI-style format check

uv run mypy                        # Type check (configured via pyproject.toml)
```

Ruff is configured with `line-length = 120`, `target-version = "py313"`, and a broad rule set (`A`, `ARG`, `ASYNC`, `B`, `E`/`W`, `F`, `N`, `RUF`, `RET`, `Q`, `T20`, `COM`, `D`, `PTH`, `SLF`, `FIX`, plus `I` for isort). mypy runs with the SQLAlchemy plugin and `strict_equality`.

### Building the package

```bash
python -m pip install build
python -m build
```

Hatchling reads the version from `src/expenses_counter/__init__.py:__version__`.

## Testing

Tests live in `backend/tests/` and run with **pytest** + **pytest-asyncio** + **pytest-cov**. See `tests/README.md` for the fixture catalogue.

```bash
uv run pytest                         # full suite with coverage
uv run pytest tests/api               # API endpoint tests
uv run pytest tests/integrational     # Integration tests
uv run pytest -m "not slow"           # Skip slow tests
uv run pytest -m api                  # Only API-tagged tests
```

Layout:

- `tests/conftest.py` — session/function fixtures (temporary SQLite DB, `AsyncDatabaseClient`, rolled-back `db_session`).
- `tests/test_*.py` — unit tests for the database client, `BaseDAO`, and `Filter`.
- `tests/api/` — endpoint tests.
- `tests/integrational/api/` — integration tests across multiple endpoints.
- `tests/auth/` — JWT / password tests.
- `tests/web_crawler/` — crawler/parser tests.

Configured pytest options (from `pyproject.toml`): `asyncio_mode = "auto"`, session-scoped event loop, strict markers (`asyncio`, `slow`, `integration`, `api`), HTML coverage report in `htmlcov/`. Coverage omits `tests/`, `alembic/`, and `utils/cli/`.

## Notebooks

`backend/notebooks/` contains Jupyter notebooks that exercise the codebase interactively (kernel: `ipykernel`, installed as a dev dependency):

- `app_config.ipynb` — load and inspect `AppConfig`.
- `auth.ipynb` — explore `PasswordService` / `JWTTokenService`.
- `daos.ipynb` — DAO usage examples.
- `web_crawler.ipynb` — drive the receipt crawler against sample URLs.

## Architecture Highlights

- **Application factory**: `expenses_counter.modules.app:get_app` builds a configured `FastAPI` instance (CORS, lifespan, static mount, routers). `__main__.py` and the `run` CLI command both invoke it through `uvicorn.run(..., factory=True)`.
- **Singletons**: `AppConfig` and `AsyncDatabaseClient` are singletons via `expenses_counter.utils.singleton.Singleton`.
- **DI**: FastAPI dependencies in `modules/middlewares/dependencies/` wire the DB client (`get_db`), DAOs (`daos/`), config (`get_config`), and auth (`user_authorized`, `admin_required`).
- **Type-safe DAOs**: `BaseDAO[DatabaseModel: Base]` uses a single PEP 695 generic to keep DAO subclasses statically typed.
- **Async end-to-end**: every database call, DAO, and route handler is `async`; SQLite gets `PRAGMA foreign_keys=ON` automatically.
- **Filter abstraction**: `utils/filter.py` translates JSON-style filter dicts into SQLAlchemy `WHERE` clauses for list endpoints.

## License

MIT — see `LICENSE`.
