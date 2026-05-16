"""Tests for ``Crawler``.

The full ``run()`` flow requires a real Chrome browser and a reachable receipt
URL, so it is gated on the ``CRAWLER_TEST_URL`` environment variable. When the
variable is unset, the live test is skipped; when set, the crawler is pointed
at that URL and the result is asserted to be a valid ``CrawledDataStorage``.

The lightweight option-construction test runs unconditionally because it
inspects pure Python without spawning a browser.
"""

import os

import pytest

from expenses_counter.utils.web_crawler import Crawler
from expenses_counter.utils.web_crawler.models import CrawledDataStorage

_CRAWLER_TEST_URL_ENV = "CRAWLER_TEST_URL"


class TestChromeOptions:
    """``chrome_options`` returns headless-safe defaults used by ``run()``."""

    def test_headless_flag_is_set(self) -> None:
        """The new headless implementation is enabled for non-interactive runs."""
        options = Crawler(url="http://example.com").chrome_options
        assert "--headless=new" in options.arguments

    def test_sandbox_is_disabled_for_container_compatibility(self) -> None:
        """``--no-sandbox`` is required for containerized Chrome."""
        options = Crawler(url="http://example.com").chrome_options
        assert "--no-sandbox" in options.arguments

    def test_dev_shm_usage_is_disabled_for_stability(self) -> None:
        """``--disable-dev-shm-usage`` avoids ``/dev/shm`` exhaustion in containers."""
        options = Crawler(url="http://example.com").chrome_options
        assert "--disable-dev-shm-usage" in options.arguments


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.skipif(
    not os.environ.get(_CRAWLER_TEST_URL_ENV),
    reason=f"{_CRAWLER_TEST_URL_ENV} env var is not set; skipping live crawler test",
)
class TestRunIntegration:
    """End-to-end crawl against a live receipt URL provided via ``CRAWLER_TEST_URL``."""

    def test_run_returns_validated_crawled_data_storage(self) -> None:
        """A live crawl must produce a ``CrawledDataStorage`` that passes ``validate``."""
        url = os.environ[_CRAWLER_TEST_URL_ENV]
        data = Crawler(url=url).run()

        assert isinstance(data, CrawledDataStorage)
        # The crawled receipt should be self-consistent end-to-end.
        data.validate()
        assert not data.df.empty
        assert data.html_parser.shop_name
        assert data.html_parser.street_address
