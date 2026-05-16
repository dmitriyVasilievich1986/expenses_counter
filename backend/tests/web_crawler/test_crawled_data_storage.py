"""Unit tests for ``CrawledDataStorage``."""

import pytest

from expenses_counter.utils.web_crawler.models import CrawledDataStorage

from .conftest import ReceiptExpectation


class TestConstruction:
    """``CrawledDataStorage`` aggregates the HTML parser and the table parser."""

    def test_exposes_both_parsers(self, mock_receipt_html: str) -> None:
        """``html_parser`` and ``df`` are populated from the same input HTML."""
        storage = CrawledDataStorage(html=mock_receipt_html)
        assert storage.html_parser is not None
        assert storage.df is not None
        assert storage.html == mock_receipt_html

    def test_str_includes_metadata_and_table(self, mock_receipt: ReceiptExpectation) -> None:
        """``__str__`` concatenates the HTML metadata block and the table representation."""
        storage = CrawledDataStorage(html=mock_receipt.html)
        rendered = str(storage)
        assert mock_receipt.shop_name in rendered
        assert mock_receipt.address in rendered
        # Each parsed item name appears in the table portion of the output
        for name, _, _ in mock_receipt.items:
            assert name in rendered


class TestValidate:
    """``validate()`` cross-checks completeness and total-vs-sum agreement."""

    def test_passes_on_consistent_mock_receipt(self, mock_receipt_html: str) -> None:
        """The default mock is internally consistent and validates cleanly."""
        storage = CrawledDataStorage(html=mock_receipt_html)
        storage.validate()  # Must not raise

    def test_raises_when_table_is_empty(self) -> None:
        """An empty product table (headers only, no rows) fails validation."""
        html = """
        <html><body>
          <span id="sdcDateTimeLabel">20/01/2026 10:30:00 AM</span>
          <span id="addressLabel">123 Main Street</span>
          <span id="shopFullNameLabel">Test Shop</span>
          <span id="totalAmountLabel">0.00</span>
          <table>
            <thead><tr>
              <th>Name</th><th>Quantity</th><th>Gross Unit Price</th>
            </tr></thead>
            <tbody></tbody>
          </table>
        </body></html>
        """
        storage = CrawledDataStorage(html=html)
        with pytest.raises(ValueError, match="Table parser is empty"):
            storage.validate()

    def test_raises_when_date_span_is_missing(self, mock_receipt_html: str) -> None:
        """Missing ``sdcDateTimeLabel`` surfaces through the parser during validation."""
        broken_html = mock_receipt_html.replace('id="sdcDateTimeLabel"', 'id="other"')
        storage = CrawledDataStorage(html=broken_html)
        with pytest.raises(ValueError, match="Date span not found"):
            storage.validate()

    def test_raises_when_address_span_is_missing(self, mock_receipt_html: str) -> None:
        """Missing ``addressLabel`` surfaces through the parser during validation."""
        broken_html = mock_receipt_html.replace('id="addressLabel"', 'id="other"')
        storage = CrawledDataStorage(html=broken_html)
        with pytest.raises(ValueError, match="Address span not found"):
            storage.validate()

    def test_raises_when_total_span_is_missing(self, mock_receipt_html: str) -> None:
        """Missing ``totalAmountLabel`` surfaces through the parser during validation."""
        broken_html = mock_receipt_html.replace('id="totalAmountLabel"', 'id="other"')
        storage = CrawledDataStorage(html=broken_html)
        with pytest.raises(ValueError, match="Total price span not found"):
            storage.validate()

    def test_raises_when_total_does_not_match_table_sum(self, mock_receipt_html: str) -> None:
        """A total that diverges from the line-item sum by more than 1 is rejected."""
        # Real sum is 25.50; bump the declared total to 999.99 to force a mismatch.
        broken_html = mock_receipt_html.replace(
            '<span id="totalAmountLabel">25.50</span>',
            '<span id="totalAmountLabel">999.99</span>',
        )
        storage = CrawledDataStorage(html=broken_html)
        with pytest.raises(ValueError, match="Total price does not match"):
            storage.validate()

    def test_passes_when_total_is_within_one_unit_of_table_sum(self, mock_receipt_html: str) -> None:
        """Differences of <= 1 currency unit are tolerated (rounding allowance)."""
        # Real sum is 25.50; bump the declared total to 26.40 -> diff 0.90 <= 1.
        adjusted_html = mock_receipt_html.replace(
            '<span id="totalAmountLabel">25.50</span>',
            '<span id="totalAmountLabel">26.40</span>',
        )
        storage = CrawledDataStorage(html=adjusted_html)
        storage.validate()  # Must not raise
