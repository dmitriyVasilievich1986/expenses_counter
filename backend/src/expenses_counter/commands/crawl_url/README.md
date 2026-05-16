# Crawl URL Commands

Command-pattern wrappers that turn crawled receipt pages into persisted database records.

This module bridges the [`web_crawler`](../../utils/web_crawler/README.md) utility and the application's DAO layer: a crawl produces a `CrawledDataStorage`, and a command in this package validates that payload, resolves the relevant store/category, and writes one `Transaction` per line item for a given `User`.

## Components

| Component | Responsibility |
| --- | --- |
| `CrawlAndCreateCommand` | Persists a `CrawledDataStorage` payload as products + transactions owned by a `User`. Resolves the receipt's `Address` from the parsed shop name and inherits the shop's `category_id` for any product that has to be created on the fly. |

`CrawlAndCreateCommand` extends `BaseCommand` and follows its three-step lifecycle:

1. **`initialize()`** — lazily constructs an `AsyncDatabaseClient` from `AppConfig` if one was not injected, and logs the bound user.
2. **`validate()`** — calls `CrawledDataStorage.validate()` for end-to-end sanity checks, then looks up the `Address` by the crawled shop's `local_name` and sets `category_id` from the matched address's shop.
3. **`execute()`** — iterates the parsed `DataFrame` and, for each row, fetches the matching `Product` (creating it under the resolved `category_id` if absent) and writes a `Transaction` with the receipt date, quantity, unit price, and user.

## Requirements

- Backend dependencies installed via `uv sync` (see the [backend instructions](../../../../../README.md) and root `CLAUDE.md`).
- A populated database: the resolved `Address` (matched by the crawled `shop_name` as `local_name`) and the acting `User` must already exist. Run migrations with `uv run alembic upgrade head` and seed/create the user beforehand.
- A valid `AppConfig` (loaded automatically from `backend/configurations/`).

## Usage

### CLI

The command is wired into the main CLI under the `crawler` group as `crawl-and-create`:

```bash
# From the backend/ directory
uv run expenses_counter crawler crawl-and-create \
    --url "https://example-receipt-host/receipt/12345" \
    --username "alice"
```

Flags:

- `--url` (required) — Receipt page URL to crawl.
- `--username` (required) — Username of the `User` who will own the created `Transaction` rows.

To inspect what would be persisted without writing to the database, use the sibling `crawl-url` command, which prints the parsed `CrawledDataStorage`:

```bash
uv run expenses_counter crawler crawl-url --url "https://example-receipt-host/receipt/12345"
```

### Programmatic

`CrawlAndCreateCommand` can be invoked directly from Python — useful from notebooks, scripts, or other commands:

```python
import asyncio

from expenses_counter.commands.crawl_url import CrawlAndCreateCommand
from expenses_counter.config import AppConfig
from expenses_counter.services.daos import UserDAO
from expenses_counter.services.database import AsyncDatabaseClient
from expenses_counter.utils.web_crawler import Crawler


async def crawl_receipt(url: str, username: str) -> None:
    app_config = AppConfig.get_or_create()
    db_client = AsyncDatabaseClient(app_config=app_config)

    user = await UserDAO(db_client).get_by_username(username)
    data = Crawler(url=url).run()

    cmd = CrawlAndCreateCommand(data=data, user=user, db=db_client)
    await cmd.initialize()
    await cmd.validate()
    await cmd.execute()


asyncio.run(crawl_receipt(
    url="https://example-receipt-host/receipt/12345",
    username="alice",
))
```

### Reusing a pre-parsed payload

If you already have a `CrawledDataStorage` (e.g., constructed from saved HTML), skip `Crawler` and feed it directly to the command:

```python
from expenses_counter.commands.crawl_url import CrawlAndCreateCommand
from expenses_counter.utils.web_crawler import CrawledDataStorage

with open("receipt.html", encoding="utf-8") as f:
    data = CrawledDataStorage(html=f.read())

cmd = CrawlAndCreateCommand(data=data, user=user)  # db will be lazily created
await cmd.initialize()
await cmd.validate()
await cmd.execute()
```

### Pre-setting the address

`validate()` only resolves the `Address` automatically when `command.address` is `None`. To target a specific store explicitly (and bypass the `local_name` lookup), set both `address` and `category_id` before calling `validate()`:

```python
cmd = CrawlAndCreateCommand(data=data, user=user, db=db_client)
cmd.address = existing_address
cmd.category_id = existing_address.shop.category_id

await cmd.initialize()
await cmd.validate()  # skips the AddressDAO lookup
await cmd.execute()
```

## Errors

- `ValueError` — raised by `CrawledDataStorage.validate()` during `validate()` when the receipt is incomplete (missing metadata, empty line-items, or total mismatch).
- `sqlalchemy.exc.NoResultFound` — raised by `validate()` when no `Address` matches the crawled shop's `local_name`. Create the `Address` (and its parent `Shop`/`Category`) first, or pre-set `command.address` as shown above.

## See also

- [`utils/web_crawler/README.md`](../../utils/web_crawler/README.md) — the crawler/parsers that produce the `CrawledDataStorage` consumed here.
- [`commands/base.py`](../base.py) — the `BaseCommand` interface (`initialize` / `validate` / `execute`).
