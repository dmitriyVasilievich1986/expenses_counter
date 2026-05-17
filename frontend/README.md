# Expenses Counter Frontend

A React 19 + TypeScript single-page application that consumes the [Expenses Counter backend](../backend/README.md). It provides authenticated UI for managing expense transactions, shops, products, and categories, plus charts for monthly spend and most-popular products.

## Overview

The frontend is built with Vite, talks to the FastAPI backend over JWT-authenticated Axios calls, and stores client state in lightweight Zustand stores. The production build is emitted directly into `../backend/static/`, where the backend serves it as the application root — there is no separate frontend hosting layer.

## Features

- **JWT authentication**: login form exchanges credentials for an access token stored as a cookie; an Axios request interceptor injects `Authorization: Bearer <jwt>` on every API call and redirects to `/login?redirectTo=...` when the cookie is missing.
- **Transactions**: per-day calendar view with a left-side filter pane, a creation form, and a right-side detail view.
- **CRUD pages** for shops, products (with an embedded price-history chart), and category browsing.
- **Statistics dashboard** on the home page: monthly spendings chart and most-popular-products list (powered by `@mui/x-charts`).
- **Profile page** for editing the current user.
- **Material-UI 7** component library with Emotion-based styling, plus SCSS modules for layout-heavy components.
- **Code-split routes**: every page is `lazy()`-loaded behind `<Suspense>`.
- **Path aliases** (`@components`, `@pages`, `@store`, `@services`) for clean imports.

## Tech Stack

- **Runtime**: React 19, React DOM 19, React Router 7
- **Language**: TypeScript ~5.9 (strict, `noUnusedLocals` / `noUnusedParameters` on)
- **State**: Zustand 5
- **HTTP**: Axios + `js-cookie`
- **UI**: Material-UI 7 (`@mui/material`, `@mui/icons-material`), `@mui/x-charts`, `@mui/x-date-pickers`, `@emotion/react`, `@emotion/styled`, `@fontsource/roboto`
- **Dates**: dayjs
- **Utilities**: lodash, classnames
- **Styling**: Sass (SCSS) for component-scoped styles
- **Build**: Vite 7 + `@vitejs/plugin-react`
- **Lint / format**: ESLint 9 (flat config) + `typescript-eslint`, `eslint-plugin-react-hooks`, `eslint-plugin-react-refresh`, `eslint-plugin-import`, `eslint-config-prettier`; Prettier 3

## Installation

```bash
cd frontend
npm install
```

## Running

The Vite dev server proxies module requests live; build output goes to the backend `static/` directory.

```bash
# Dev server (http://localhost:5173 by default)
npm run dev

# Production build → ../backend/static/assets/*
npm run build

# Preview the production build locally
npm run preview
```

The repo also ships `scripts/start.sh` which simply runs `npm i && npm run build` — useful for container builds.

### Environment

The Axios client reads its base URL from the `VITE_API_HOST` environment variable. The repo ships a default `.env`:

```env
VITE_API_HOST=http://localhost:8000
```

Vite also injects `import.meta.env.VITE_APP_VERSION` from `application-version.json` at build time.

### Backend integration

`vite.config.ts` sets `build.outDir` to `../backend/static` with `emptyOutDir: false`, so the build emits `assets/[name]-[hash].(js|css)` directly into the backend's static-files directory. The backend (`backend/src/expenses_counter/utils/mount_static_files.py`) mounts that folder as the SPA root. `index.html` references the icon at `/static/images/favicon.svg`, served from the same backend tree.

## Project Structure

```
frontend/
├── application-version.json     # Version string, exposed as VITE_APP_VERSION
├── index.html                   # Vite HTML entry (loads src/main.tsx)
├── vite.config.ts               # Vite build, path aliases, output dir
├── tsconfig.json                # TS project references (app + node)
├── tsconfig.app.json            # App-side TS config + path aliases
├── tsconfig.node.json           # Vite config TS settings
├── eslint.config.js             # ESLint flat config
├── .prettierrc                  # Prettier rules
├── .env                         # VITE_API_HOST (gitignored override possible)
├── scripts/
│   └── start.sh                 # npm i && npm run build
└── src/
    ├── main.tsx                 # React root: StrictMode + BrowserRouter
    ├── App.tsx                  # Navbar + Routes
    ├── index.css / App.css      # Minimal global styles
    ├── vite-env.d.ts            # Vite client types
    ├── components/              # Reusable UI (Navbar, Card, Input, …)
    ├── pages/                   # Route-level pages (home, login, shop, …)
    ├── services/
    │   └── apiClient/           # Axios instance + per-resource hooks
    └── store/                   # Zustand stores (main, product, transaction, …)
```

## Routing

Routes live in `src/App.tsx`. Pages are lazy-loaded behind `Suspense`:

| Path                          | Page              | Notes                                          |
| ----------------------------- | ----------------- | ---------------------------------------------- |
| `/`                           | `Home`            | Charts: monthly spend + most popular products. |
| `/login`                      | `Login`           | Username/password form → JWT cookie.           |
| `/profile`                    | `Profile`         | View / edit the current user.                  |
| `/shop`                       | `ShopList`        | Paginated shop list.                           |
| `/shop/create`                | `CreateShop`      | Create form.                                   |
| `/shop/:shopId`               | `CreateShop`      | Edit form (same component, ID-aware).          |
| `/product`                    | `ProductList`     | Paginated product list.                        |
| `/product/create`             | `CreateProduct`   | Create form.                                   |
| `/product/:productId`         | `CreateProduct`   | Edit form.                                     |
| `/transaction`                | `TransactionPage` | Calendar + filters + creation.                 |
| `/transaction/:transactionId` | `TransactionPage` | Same view, focused on one row.                 |

There is no route-level auth guard; the Axios request interceptor enforces auth by redirecting to `/login?redirectTo=<current-path>` whenever the `accessToken` cookie is missing.

## API Client (`src/services/apiClient/`)

A single Axios instance (`base.ts`) is shared by every per-resource hook:

```ts
export const apiClientInstance = axios.create({
  baseURL: import.meta.env.VITE_API_HOST,
  headers: { 'Content-Type': 'application/json' },
});

apiClientInstance.interceptors.request.use((config) => {
  const accessToken = Cookies.get('accessToken');
  if (!accessToken) {
    window.location.href = `/login?redirectTo=${encodeURIComponent(window.location.pathname)}`;
    throw new Error('Unauthorized');
  }
  config.headers.Authorization = `Bearer ${accessToken}`;
  return config;
});
```

`useApiClientWrapper` flips the global `isLoading` flag on `useMainStore` around any request so the UI can render a global spinner.

Per-resource hooks (each file: `client.ts`, `types.ts`, `index.ts`):

| Hook                      | Endpoints                                                                                           |
| ------------------------- | --------------------------------------------------------------------------------------------------- |
| `useAuthAPIClient`        | `POST /api/login` (uses raw `axios`, no interceptor — no token yet)                                 |
| `useCategoryAPIClient`    | `GET/POST/PUT/PATCH/DELETE /api/v1/category`                                                        |
| `useShopAPIClient`        | `/api/v1/shop` CRUD                                                                                 |
| `useAddressAPIClient`     | `/api/v1/address` CRUD                                                                              |
| `useProductAPIClient`     | `/api/v1/product` CRUD                                                                              |
| `useTransactionAPIClient` | `/api/v1/transaction` CRUD                                                                          |
| `useStatisticsAPIClient`  | `GET /api/v1/statistics/spendings/grouped-by-month`, `GET /api/v1/statistics/most-popular-products` |
| `useUserAPIClient`        | `/api/v1/user` (profile, current user)                                                              |

Mutating hooks (create/update/delete) sync the result into the matching Zustand store so list views stay consistent.

## State Management (`src/store/`)

State uses **Zustand** (not Redux) with Redux DevTools middleware for inspection.

| Store                 | Responsibility                                                                     |
| --------------------- | ---------------------------------------------------------------------------------- |
| `useMainStore`        | Global `isLoading` flag and the authenticated `user`.                              |
| `useCategoryStore`    | Category tree + per-entity mutations.                                              |
| `useShopStore`        | Shop list and `currentShop`.                                                       |
| `useProductStore`     | Paginated product list and `currentProduct`.                                       |
| `useTransactionStore` | Transaction list, calendar-selected `currentDate` (`dayjs`), `currentTransaction`. |

Each store exports a hook (`use<Name>Store`) and a `types.ts` with its model. The API client hooks call these stores' setters directly after a successful mutation.

## Authentication Flow

1. **Login**: `src/pages/login/Login.tsx` submits `{ username, password }` to `POST /api/login` via `useAuthAPIClient`.
2. **Token storage**: the response (`access_token`, `expires_at`) is stored in a cookie named `accessToken` using `js-cookie`, with the expiry returned by the backend.
3. **Authenticated requests**: every subsequent call goes through `apiClientInstance`, whose request interceptor reads the cookie and adds `Authorization: Bearer <jwt>`.
4. **Unauthenticated redirect**: if the cookie is missing when a request fires, the interceptor sends the browser to `/login?redirectTo=<current-path>`.
5. **Logout**: `src/components/navbar/logout/Logout.tsx` removes the cookie and navigates to `/login`.

## Components (`src/components/`)

Re-exported from `src/components/index.ts` for use via `@components`:

| Component      | Purpose                                                    |
| -------------- | ---------------------------------------------------------- |
| `Navbar`       | Top bar: logo, primary navigation, logout.                 |
| `Card`         | Generic card surface.                                      |
| `CardsStack`   | Stacked layout for card lists.                             |
| `Input`        | Form input wrapper.                                        |
| `AsyncInput`   | Input with async option loading (autocomplete-style).      |
| `SubmitButton` | Submit button with a loading state tied to `useMainStore`. |

Additional internal pieces live in their own subfolders: `avatar/`, `image/`, `search/`, `productPriceChart/`, plus `navbar/logout/`. SCSS modules sit next to the components that use them (e.g. `navbar/style.scss`, `card/style.scss`).

## Path Aliases

Declared in both `vite.config.ts` and `tsconfig.app.json`:

| Alias         | Resolves to      |
| ------------- | ---------------- |
| `@components` | `src/components` |
| `@pages`      | `src/pages`      |
| `@store`      | `src/store`      |
| `@services`   | `src/services`   |

Each alias has a bare form (`@components`) that hits the barrel `index.ts`, and a wildcard form (`@components/*`) for deep imports.

## Linting & Formatting

```bash
npm run lint:check       # ESLint (errors only, no fixes)
npm run lint:fix         # ESLint with --fix
npm run format:check     # Prettier --check on the whole repo
npm run format:fix       # Prettier --write
```

ESLint (`eslint.config.js`) uses the flat-config format:

- Extends `@eslint/js` recommended, `typescript-eslint` recommended, and `eslint-config-prettier` (turns off stylistic rules).
- Enables `react-hooks` rules but disables `exhaustive-deps`.
- `react-refresh/only-export-components` warns on barrels that mix exports.
- `@typescript-eslint/no-unused-vars` errors except on `_`-prefixed names.
- `eslint-plugin-import` enforces a strict import order: builtins/externals → internal aliases → relative → object → type, with a single blank line between groups and case-insensitive alphabetical ordering.

Prettier (`.prettierrc`): semicolons, single quotes, ES5 trailing commas, 100-char print width, 2-space indent, always-parenthesised arrows.

## Build Output

`vite.config.ts` writes:

```
../backend/static/
└── assets/
    ├── index-<hash>.js
    ├── index-<hash>.css
    └── <chunk>-<hash>.js
```

`emptyOutDir: false` preserves anything the backend ships under `static/` (e.g. favicons, server-side images) across builds. `index.html` is also emitted at the static root and served by the FastAPI app.

## Testing

There is no test suite yet. No runner (Jest, Vitest, Playwright) is wired up in `package.json`.

## Notably Absent

- No Redux or Redux Toolkit — state is entirely Zustand-based.
- No i18n / translations.
- No service worker or PWA manifest.
- No mock data fixtures or MSW setup.
- No route-level auth guard component — auth is enforced at the HTTP layer.
