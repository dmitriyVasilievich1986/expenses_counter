# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

For deep dives, prefer the package READMEs over duplicating their content here:

- [`backend/README.md`](backend/README.md) — backend services, CLI, config, API, testing.
- [`frontend/README.md`](frontend/README.md) — Vite/React app, routes, stores, auth flow.
- [`backend/tests/README.md`](backend/tests/README.md) — pytest fixtures and test layout.
- [`backend/src/expenses_counter/services/auth/README.md`](backend/src/expenses_counter/services/auth/README.md) — `PasswordService` / `JWTTokenService`.
- [`backend/src/expenses_counter/utils/web_crawler/README.md`](backend/src/expenses_counter/utils/web_crawler/README.md) — receipt crawler internals.
- [`backend/src/expenses_counter/commands/crawl_url/README.md`](backend/src/expenses_counter/commands/crawl_url/README.md) — crawl-to-transactions command.

## Project Overview

Expenses Counter is a full-stack expense tracker. The backend exposes a JWT-secured REST API for users, categories, shops, addresses, products, and transactions, plus statistics endpoints and a Selenium-based receipt crawler. The frontend is a React SPA that consumes that API and is built directly into the backend's `static/` directory.

**Tech stack:**

- **Backend**: Python 3.13, FastAPI, SQLAlchemy 2.0 (async), Pydantic v2 + pydantic-settings, Alembic, PyJWT, bcrypt, Selenium + BeautifulSoup, Loguru, asyncclick.
- **Frontend**: React 19, TypeScript ~5.9, React Router 7, Material-UI 7 + MUI X Charts/Date-Pickers, Emotion, Zustand 5, Axios, js-cookie, dayjs, Sass.
- **Build / tooling**: `uv` (Python), Vite 7 (JS), Alembic (DB migrations), Ruff + mypy (Python), ESLint flat config + Prettier (JS), pytest + pytest-asyncio + pytest-cov.
- **Databases**: PostgreSQL (asyncpg/psycopg) for production, SQLite (aiosqlite) for dev/tests.

## Development Commands

### Backend

Run from `backend/`. Uses **uv** for environments. The `expenses_counter` console script (defined in `pyproject.toml` `[project.scripts]`) is the canonical entry point.

```bash
uv sync                                # install + create .venv
source .venv/bin/activate              # optional; `uv run` works without it

# Server
uv run expenses_counter run                                # 0.0.0.0:8000
uv run expenses_counter run --reload                       # dev mode
uv run expenses_counter run --host 127.0.0.1 --port 9000

# Config
uv run expenses_counter show-config                        # dump resolved config

# User management
uv run expenses_counter user create-user --username alice --email alice@example.com
uv run expenses_counter user check-password --username alice
uv run expenses_counter user generate-jwt-token --username alice
uv run expenses_counter user re-generate-password --username alice

# Database
uv run expenses_counter db migrate-db                      # alembic upgrade head
uv run expenses_counter db migrate-db --revision <rev>
uv run expenses_counter db downgrade-db --revision <rev>
uv run expenses_counter db fill-db                         # seed sample data

# Receipt crawler
uv run expenses_counter crawler crawl-url --url <receipt-url>
uv run expenses_counter crawler crawl-and-create --url <receipt-url> --username alice

# Raw Alembic (still works)
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head
uv run alembic downgrade -1
uv run alembic history

# Code quality
uv run ruff check src/         # lint
uv run ruff check --fix src/   # auto-fix
uv run ruff format src/        # format
uv run ruff format --check src/
uv run mypy                    # type check (configured in pyproject.toml)

# Tests (pytest + pytest-asyncio + pytest-cov, configured in pyproject.toml)
uv run pytest                             # full suite + coverage
uv run pytest tests/api                   # endpoint tests
uv run pytest tests/integrational         # integration tests
uv run pytest -m "not slow"
uv run pytest -m api

# Build package
uv build
```

### Frontend

Run from `frontend/`. Vite (not webpack) drives both dev and prod builds.

```bash
npm install
# or: npm ci   (clean install from package-lock.json, CI-friendly)

npm run dev            # Vite dev server, http://localhost:5173
npm run build          # tsc -b && vite build → ../backend/static/assets/*
npm run preview        # serve the production build locally

npm run lint:check     # ESLint
npm run lint:fix       # ESLint --fix
npm run format:check   # Prettier --check .
npm run format:fix     # Prettier --write .
```

**Build output**: `vite.config.ts` writes to `../backend/static/` with `emptyOutDir: false` and a Rollup config that emits `assets/[name]-[hash].(js|css)`. The backend mounts that directory at the SPA root via `expenses_counter.utils.mount_static_files` — there is no separate frontend host.

The `VITE_API_HOST` env var (default in `frontend/.env`: `http://localhost:8000`) configures the API base URL. `VITE_APP_VERSION` is injected from `frontend/application-version.json` at build time.

## Architecture

### Backend layout

```
backend/src/expenses_counter/
├── __init__.py                # __version__
├── __main__.py                # python -m expenses_counter entrypoint
├── commands/                  # Reusable command objects
│   ├── fill_db/               # Seed sample data
│   └── crawl_url/             # Crawl receipt → Transaction rows
├── config/                    # AppConfig singleton + Pydantic config models
│   └── models/
│       ├── info/              # api / cors / paths
│       └── services/          # auth / database
├── modules/                   # FastAPI app layer
│   ├── app.py                 # get_app() factory
│   ├── middlewares/           # lifespan + DI dependencies (auth, daos, db, config)
│   └── routers/
│       ├── api/v1/            # address, category, product, shop, transaction,
│       │                      # statistics, user
│       ├── system/            # health, version, login, index
│       └── schemas/           # requests/ + responses/ Pydantic models
├── services/                  # Business logic
│   ├── alembic/               # env.py + versions/
│   ├── auth/                  # JWTTokenService, PasswordService
│   ├── daos/                  # Address/Category/Product/Shop/Transaction/User
│   └── database/              # AsyncDatabaseClient + ORM models
└── utils/                     # filter, mount_static_files, singleton,
                               # cli/, web_crawler/
```

**Key architectural patterns:**

1. **Application factory**: `expenses_counter.modules.app:get_app` builds the `FastAPI` instance with CORS, lifespan, static mount, and routers. Both `__main__.py` and the `run` CLI use `uvicorn.run(..., factory=True)`.
2. **Singletons**: `AppConfig` and `AsyncDatabaseClient` use `expenses_counter.utils.singleton.Singleton` to ensure single instances.
3. **DAO pattern**: each entity has a DAO; all inherit from `BaseDAO[DatabaseModel: Base]` (PEP 695 single-parameter generic). A DAO accepts either an `AsyncDatabaseClient` (opens short-lived sessions) or an injected `AsyncSession`.
4. **Pydantic schemas per DAO**: `Get` (response), `Post` (create), `Put` (full update), `Patch` (partial update). They live under `modules/routers/schemas/requests/` and `.../responses/`.
5. **Async end-to-end**: every database call, DAO, route handler, and CLI command is `async`. SQLite gets `PRAGMA foreign_keys=ON` automatically when the engine connects.
6. **Auth via dependencies**: protected routes depend on `user_authorized` (`modules/middlewares/dependencies/user_authorized.py`); admin-only routes additionally depend on `admin_required`.

### Database models & relationships

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

Models live in `services/database/models/` (`user.py`, `category.py`, `shop.py`, `address.py`, `product.py`, `transaction.py`, plus `base.py`). Table names are prefixed with `main_` (e.g. `main_user`, `main_transaction`).

### API endpoints

All v1 endpoints are mounted under `/api/v1/` and require `Authorization: Bearer <jwt>`. Some destructive endpoints additionally require admin privileges.

For each of `address`, `category`, `product`, `shop`, `transaction`, `user`:

- `GET    /api/v1/{entity}`           — list (with filters / pagination)
- `GET    /api/v1/{entity}/{id}`      — single resource
- `POST   /api/v1/{entity}`           — create
- `PUT    /api/v1/{entity}/{id}`      — full update
- `PATCH  /api/v1/{entity}/{id}`      — partial update
- `DELETE /api/v1/{entity}/{id}`      — delete (admin-only on most entities)

Notable extras:

- `GET /api/v1/category/by-shop/{shop_id}`
- `GET /api/v1/address/name/{local_name}`
- `GET /api/v1/user/me`
- `GET /api/v1/statistics/spendings/grouped-by-month`
- `GET /api/v1/statistics/most-popular-products`

System endpoints under `/api`:

- `POST /api/login` — exchange `{username, password}` for `{access_token, expires_at}`.
- `GET  /api/health` — database connectivity check.
- `GET  /api/version` — package version.
- `GET  /api/` — index.

Interactive docs: `http://localhost:8000/docs`.

### Frontend layout

```
frontend/
├── application-version.json    # exposed as VITE_APP_VERSION
├── index.html                  # Vite HTML entry
├── vite.config.ts              # build config + path aliases
├── tsconfig.{json,app.json,node.json}
├── eslint.config.js            # flat config
├── .prettierrc
├── .env                        # VITE_API_HOST
├── scripts/start.sh            # npm i && npm run build
└── src/
    ├── main.tsx                # React root + BrowserRouter
    ├── App.tsx                 # Navbar + lazy-loaded routes
    ├── components/             # Reusable UI (Navbar, Card, Input, AsyncInput, …)
    ├── pages/                  # home, login, profile, shop, product, transaction
    ├── services/apiClient/     # Axios instance + per-resource hooks
    └── store/                  # Zustand stores (main, category, shop, product, transaction)
```

**Key frontend patterns:**

- **State**: Zustand with Redux DevTools middleware. Stores expose hooks (`useMainStore`, `useProductStore`, etc.) and are mutated directly by API client hooks after successful requests.
- **HTTP**: a single Axios instance (`services/apiClient/base.ts`) with a request interceptor that reads the `accessToken` cookie (`js-cookie`) and injects `Authorization: Bearer <jwt>`. If the cookie is missing, the interceptor redirects to `/login?redirectTo=<current-path>` — there is no route-level auth guard.
- **Routing**: React Router 7 in `App.tsx`. Pages are `lazy()`-loaded behind `<Suspense>`. Routes: `/`, `/login`, `/profile`, `/shop` (+ `/create` and `/:shopId`), `/product` (+ `/create` and `/:productId`), `/transaction` (+ `/:transactionId`).
- **Path aliases** (declared in both `vite.config.ts` and `tsconfig.app.json`): `@components`, `@pages`, `@store`, `@services` — bare form hits the barrel `index.ts`, `@x/*` for deep imports.
- **Styling**: Material-UI 7 + Emotion; component-scoped Sass (`.scss`) files alongside components; minimal global CSS in `src/index.css` and `src/App.css`.

### Configuration system

The `AppConfig` singleton (`expenses_counter.config.AppConfig`) is built by `pydantic-settings` from a YAML file plus environment variables. The YAML file is selected via the `CONFIG_FILE_PATH` env var; `backend/configurations/` ships `local.yaml` and `prod.yaml`.

Sections:

- **`info.api_info`** — title, description, debug flag, log level.
- **`info.cors_info`** — allowed origins / methods / headers / credentials.
- **`info.paths_info`** — `alembic_ini`, static-files path.
- **`services.database`** — provider (`postgresql+asyncpg` or `sqlite+aiosqlite`), host, port, name, user, password; exposes a `url` property used by `AsyncDatabaseClient`.
- **`services.auth`** — `jwt_secret_key` (`SecretStr`), `password_secret_key` (`SecretStr`), `jwt_algorithm` (`HS256` | `HS384` | `HS512`).

Environment overrides use nested keys (`SECTION__SUBSECTION__FIELD`). Two example env files at `backend/`:

- `.env` — app secrets and `CONFIG_FILE_PATH`.
- `db.env` — database connection vars.

Configuration is accessed through `AppConfig.get_or_create()`.

### Version management

The backend version lives in `backend/src/expenses_counter/__init__.py` (`__version__`); Hatchling reads it via `[tool.hatch.version]`. The frontend version lives in `frontend/application-version.json` and is injected into the bundle as `VITE_APP_VERSION`.

`.github/scripts/bump_version.py` bumps both:

- on `development`: PATCH
- on `master`: MINOR (PATCH reset to 0)

## CI/CD

GitHub Actions workflows in `.github/workflows/` (all trigger on push/PR to `master` or `development` and skip when path filters detect no relevant changes):

- **`build_backend.yml`** — `uv sync --frozen --dev`, `ruff check src/`, `ruff format --check src/`, `mypy`, `uv build`.
- **`test_backend.yml`** — `uv sync --all-groups`, `pytest`, uploads the HTML coverage report as an artifact.
- **`build_frontend.yml`** — `npm ci`, `npm run build`, uploads `frontend-build` artifacts.
- **`build_docker.yml`** — builds the Docker image with Buildx when backend/frontend/docker files change.

## Code style

**Python (backend):**

- Ruff configured in `backend/pyproject.toml`. Line length 120, `target-version = "py313"`.
- Rule set: `A`, `ARG`, `ASYNC`, `B`, `E`/`W`, `F`, `N`, `RUF`, `RET`, `Q`, `T20`, `COM`, `D`, `PTH`, `SLF`, `FIX`, plus `I` (isort).
- Import order: future → stdlib → third-party → first-party (`expenses_counter`) → local-folder.
- Docstrings required on modules, classes, and public methods (pydocstyle `D`).
- mypy runs with the SQLAlchemy plugin and `strict_equality`; plugins/types configured in `pyproject.toml`.

**TypeScript (frontend):**

- TS strict mode (`strict`, `noUnusedLocals`, `noUnusedParameters`) configured in `tsconfig.app.json`. Target `ES2022`, JSX `react-jsx`, bundler module resolution.
- ESLint flat config (`eslint.config.js`) extends `@eslint/js` recommended, `typescript-eslint` recommended, and `eslint-config-prettier`. Enables `react-hooks` (with `exhaustive-deps` off) and `react-refresh/only-export-components`. `eslint-plugin-import` enforces a strict import order with one blank line between groups and alphabetical, case-insensitive ordering.
- Prettier (`.prettierrc`): semicolons, single quotes, ES5 trailing commas, 100-char print width, 2-space indent, always-parenthesised arrows.

## Database

- Production: PostgreSQL (asyncpg as primary driver, psycopg installed alongside).
- Dev / tests: SQLite (aiosqlite). The async client toggles `PRAGMA foreign_keys=ON` automatically.
- Connection URL is built from `AppConfig.services.database` and exposed as `.url`.
- All models inherit from the SQLAlchemy declarative `Base`. Relationships use `selectinload` for eager loading where needed (see e.g. `CategoryDAO` which recursively loads the parent chain).

**Migration workflow:**

1. Edit models under `services/database/models/`.
2. Generate a migration: `uv run alembic revision --autogenerate -m "description"`.
3. Review the file under `services/alembic/versions/`.
4. Apply: `uv run expenses_counter db migrate-db` (or `uv run alembic upgrade head`).

## Entry points

**Backend:**

- CLI: `expenses_counter` console script → `expenses_counter.utils.cli.main:main`.
- Module: `python -m expenses_counter` → `__main__.py`.
- ASGI factory: `expenses_counter.modules.app:get_app` (for Uvicorn / Gunicorn-uvicorn with `--factory`).

**Frontend:**

- HTML entry: `frontend/index.html` → `src/main.tsx`.
- App component: `src/App.tsx`.
- Build output: `backend/static/assets/*.{js,css}` (hash-named) plus `backend/static/index.html`.

## Testing

The backend test suite lives at `backend/tests/`; see `backend/tests/README.md` for fixture details.

- Framework: **pytest** + **pytest-asyncio** (`asyncio_mode = "auto"`, session-scoped event loop) + **pytest-cov**.
- Strict markers: `asyncio`, `slow`, `integration`, `api`.
- HTML coverage report at `backend/htmlcov/`. Coverage omits `tests/`, `alembic/`, and `utils/cli/`.
- Layout: `tests/test_*.py` (unit), `tests/api/` (endpoint), `tests/integrational/api/` (integration), `tests/auth/` (JWT/password), `tests/web_crawler/`.

The frontend currently has **no test suite** — no Jest/Vitest/Playwright config in `frontend/package.json`. Don't fabricate a test command; if testing is needed, ask before adding a runner.
