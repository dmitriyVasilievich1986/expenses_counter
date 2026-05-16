"""Unit tests for ``HTMLParser``."""

import pytest

from expenses_counter.utils.web_crawler.models import HTMLParser

from .conftest import ReceiptExpectation


class TestMetadataExtraction:
    """``HTMLParser`` exposes the receipt's date, address, shop name, and total."""

    def test_date_is_parsed_from_sdc_date_time_label(self, mock_receipt: ReceiptExpectation) -> None:
        """``span#sdcDateTimeLabel`` is whitespace-collapsed and parsed as a datetime."""
        parser = HTMLParser(html=mock_receipt.html)
        assert parser.date == mock_receipt.date

    def test_street_address_is_stripped(self, mock_receipt: ReceiptExpectation) -> None:
        """Leading/trailing whitespace inside ``span#addressLabel`` is removed."""
        parser = HTMLParser(html=mock_receipt.html)
        assert parser.street_address == mock_receipt.address

    def test_shop_name_is_extracted_from_shop_full_name_label(self, mock_receipt: ReceiptExpectation) -> None:
        """``span#shopFullNameLabel`` provides the displayed shop name."""
        parser = HTMLParser(html=mock_receipt.html)
        assert parser.shop_name == mock_receipt.shop_name

    def test_total_price_is_parsed_via_convert_float(self, mock_receipt: ReceiptExpectation) -> None:
        """``span#totalAmountLabel`` is converted with the table parser's float rules."""
        parser = HTMLParser(html=mock_receipt.html)
        assert parser.total_price == pytest.approx(mock_receipt.total_price)

    def test_str_includes_all_metadata_lines(self, mock_receipt: ReceiptExpectation) -> None:
        """``__str__`` summarizes date, address, shop name, and total in human-readable form."""
        parser = HTMLParser(html=mock_receipt.html)
        rendered = str(parser)
        assert "Date:" in rendered
        assert mock_receipt.address in rendered
        assert mock_receipt.shop_name in rendered
        assert "Total price:" in rendered


class TestCaching:
    """Repeated property reads should return the cached value, not re-parse the HTML."""

    def test_date_is_cached_after_first_access(self, mock_receipt_html: str) -> None:
        """The second ``date`` access returns the same object as the first."""
        parser = HTMLParser(html=mock_receipt_html)
        first = parser.date
        second = parser.date
        assert first is second

    def test_address_is_cached_after_first_access(self, mock_receipt_html: str) -> None:
        """The second ``street_address`` access returns the same string."""
        parser = HTMLParser(html=mock_receipt_html)
        assert parser.street_address is parser.street_address

    def test_shop_name_is_cached_after_first_access(self, mock_receipt_html: str) -> None:
        """The second ``shop_name`` access returns the same string."""
        parser = HTMLParser(html=mock_receipt_html)
        assert parser.shop_name is parser.shop_name

    def test_total_price_is_cached_after_first_access(self, mock_receipt_html: str) -> None:
        """The second ``total_price`` access returns the same float."""
        parser = HTMLParser(html=mock_receipt_html)
        assert parser.total_price == parser.total_price


class TestMissingFields:
    """Each property raises ``ValueError`` if its source span is absent."""

    def test_date_raises_when_span_is_missing(self) -> None:
        """A missing ``sdcDateTimeLabel`` span causes ``date`` to raise."""
        parser = HTMLParser(html="<html><body></body></html>")
        with pytest.raises(ValueError, match="Date span not found"):
            _ = parser.date

    def test_street_address_raises_when_span_is_missing(self) -> None:
        """A missing ``addressLabel`` span causes ``street_address`` to raise."""
        parser = HTMLParser(html="<html><body></body></html>")
        with pytest.raises(ValueError, match="Address span not found"):
            _ = parser.street_address

    def test_shop_name_raises_when_span_is_missing(self) -> None:
        """A missing ``shopFullNameLabel`` span causes ``shop_name`` to raise."""
        parser = HTMLParser(html="<html><body></body></html>")
        with pytest.raises(ValueError, match="Shop name span not found"):
            _ = parser.shop_name

    def test_total_price_raises_when_span_is_missing(self) -> None:
        """A missing ``totalAmountLabel`` span causes ``total_price`` to raise."""
        parser = HTMLParser(html="<html><body></body></html>")
        with pytest.raises(ValueError, match="Total price span not found"):
            _ = parser.total_price
