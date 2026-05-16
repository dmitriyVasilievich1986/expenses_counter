# Web Crawler

A utility for crawling receipt pages and extracting structured transaction data (date, address, shop name, total price, and product line-items) from the rendered HTML.

The crawler uses a headless Chrome browser (via Selenium) to load a target receipt URL, switch the page to English, expand the collapsed line-item table, and snapshot the fully rendered HTML. The captured HTML is then handed off to dedicated parsers that extract receipt metadata and the product table.

## Components

| Component | Responsibility |
| --- | --- |
| `Crawler` | Drives a headless Chrome session: opens the target URL, switches language, expands collapsed UI, and returns a `CrawledDataStorage`. |
| `CrawledDataStorage` | Aggregates the raw HTML and exposes both an `HTMLParser` (metadata) and a `TableParser` (line items). Provides a `validate()` method that cross-checks metadata completeness and reconciles the receipt total against the line-item sum. |
| `HTMLParser` | Extracts receipt metadata: `date`, `street_address`, `shop_name`, `total_price`. |
| `TableParser` | A `pandas.DataFrame` subclass that parses the first receipt `<table>` into the columns `name`, `quantity`, `unit_price`, and a derived `total` (`quantity * unit_price`). |

## Requirements

- Google Chrome installed locally (the matching ChromeDriver is downloaded automatically via `webdriver_manager`).
- Python dependencies pulled in by the project: `selenium`, `webdriver-manager`, `beautifulsoup4`, `lxml`, `pandas`.

Install them through the backend's `uv` workflow:

```bash
cd backend
uv sync
```

## Usage

### Basic crawl

```python
from expenses_counter.utils.web_crawler import Crawler

url = "https://example-receipt-host/receipt/12345"

crawler = Crawler(url=url)
data = crawler.run()  # returns CrawledDataStorage

print(data)  # human-readable summary: metadata + line-item table
```

### Accessing parsed metadata

```python
from expenses_counter.utils.web_crawler import Crawler

data = Crawler(url=url).run()

print(data.html_parser.date)            # datetime object
print(data.html_parser.street_address)  # str
print(data.html_parser.shop_name)       # str
print(data.html_parser.total_price)     # float
```

### Working with the line-item table

`CrawledDataStorage.df` is a `pandas.DataFrame` (subclass `TableParser`) with the columns `name`, `quantity`, `unit_price`, and a pre-computed `total` (`quantity * unit_price`), so any pandas operation works directly:

```python
data = Crawler(url=url).run()

items_df = data.df

print(items_df.head())
print(items_df["total"].sum())

# Persist as CSV
items_df.to_csv("receipt_items.csv", index=False)
```

### Validating the crawled data

`CrawledDataStorage.validate()` performs end-to-end sanity checks on a crawl result. It raises `ValueError` when:

- the line-item table is empty,
- `date`, `street_address`, or `total_price` is missing from the HTML, or
- the HTML total and the sum of per-line `total` values differ by more than `1`.

```python
data = Crawler(url=url).run()

try:
    data.validate()
except ValueError as exc:
    print(f"Crawl rejected: {exc}")
else:
    # safe to persist into the database
    ...
```

### Parsing existing HTML without re-crawling

If you already have the rendered receipt HTML (e.g., saved to a file), you can skip Selenium and feed it directly to `CrawledDataStorage`:

```python
from expenses_counter.utils.web_crawler import CrawledDataStorage

with open("receipt.html", encoding="utf-8") as f:
    html = f.read()

data = CrawledDataStorage(html=html)

print(data.html_parser.shop_name)
print(data.df)
```

## Notes

- The crawler runs Chrome in headless mode with `--no-sandbox` and `--disable-dev-shm-usage`, which makes it suitable for containerized environments.
- The page-interaction flow (language switch, expanding the collapsed section) is tailored to the target receipt site's DOM. Changes to the source site's markup will require updating the CSS selectors in `crawler.py`.
- `TableParser.convert_float` treats values without a decimal point as minor units (divides by 100) and replaces `,` with `_` to handle thousands separators.
