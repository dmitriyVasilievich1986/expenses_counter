"""Unit tests for ``TableParser``."""

import pytest

from expenses_counter.utils.web_crawler.models import TableParser

from .conftest import ReceiptExpectation


class TestConstruction:
    """``TableParser`` is built from the first ``<table>`` of the input HTML."""

    def test_parses_mock_receipt_rows(self, mock_receipt: ReceiptExpectation) -> None:
        """Each ``<tr>`` becomes a row in the parsed DataFrame."""
        df = TableParser(html=mock_receipt.html)
        assert len(df) == len(mock_receipt.items)

    def test_columns_are_renamed_to_internal_names(self, mock_receipt_html: str) -> None:
        """``Name`` / ``Quantity`` / ``Gross Unit Price`` map to internal lowercase names."""
        df = TableParser(html=mock_receipt_html)
        assert set(df.columns) == {"name", "quantity", "unit_price", "total"}

    def test_total_column_equals_quantity_times_unit_price(self, mock_receipt: ReceiptExpectation) -> None:
        """The derived ``total`` column must equal ``quantity * unit_price`` per row."""
        df = TableParser(html=mock_receipt.html)
        for row_idx, (_, qty, price) in enumerate(mock_receipt.items):
            assert df.iloc[row_idx]["total"] == pytest.approx(qty * price)

    def test_rows_match_expected_values(self, mock_receipt: ReceiptExpectation) -> None:
        """Each parsed row carries the expected name, quantity, and unit price."""
        df = TableParser(html=mock_receipt.html)
        for row_idx, (name, qty, price) in enumerate(mock_receipt.items):
            row = df.iloc[row_idx]
            assert row["name"] == name
            assert row["quantity"] == pytest.approx(qty)
            assert row["unit_price"] == pytest.approx(price)

    def test_unrelated_columns_are_dropped(self) -> None:
        """Columns not in the canonical set must be removed from the DataFrame."""
        html = """
        <html><body><table>
          <thead><tr>
            <th>Name</th><th>Quantity</th><th>Gross Unit Price</th><th>VAT</th>
          </tr></thead>
          <tbody>
            <tr><td>Apple</td><td>2.0</td><td>5.00</td><td>1.00</td></tr>
          </tbody>
        </table></body></html>
        """
        df = TableParser(html=html)
        assert "VAT" not in df.columns


class TestConvertFloat:
    """``TableParser.convert_float`` parses receipt-style numeric strings."""

    def test_value_with_decimal_point_is_parsed_directly(self) -> None:
        """Strings containing ``.`` are converted with ``float`` unchanged."""
        assert TableParser.convert_float("5.00") == 5.0
        assert TableParser.convert_float("15.50") == 15.5

    def test_value_without_decimal_point_is_treated_as_minor_units(self) -> None:
        """Integer-only strings are divided by 100 (assumed to be cents)."""
        assert TableParser.convert_float("550") == 5.5
        assert TableParser.convert_float("100") == 1.0

    def test_comma_is_normalized_to_underscore_thousands_separator(self) -> None:
        """Commas become Python's ``_`` thousands separator so ``float`` accepts them."""
        assert TableParser.convert_float("1,250.00") == 1250.0

    def test_comma_only_value_is_still_divided_by_100(self) -> None:
        """A comma-only string has no decimal point and follows the minor-units rule."""
        assert TableParser.convert_float("1,250") == pytest.approx(12.5)

    def test_non_string_input_is_coerced_via_str(self) -> None:
        """``convert_float`` accepts arbitrary values by coercing them through ``str``."""
        assert TableParser.convert_float(5.0) == 5.0  # type: ignore[arg-type]
        assert TableParser.convert_float(550) == 5.5  # type: ignore[arg-type]
