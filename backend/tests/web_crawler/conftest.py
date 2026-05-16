"""Shared fixtures for web crawler tests.

Provides receipt-shaped mock HTML so the parser tests can run without hitting a
live receipt site. The structure mirrors what ``Crawler`` snapshots from the
target page: ``span#sdcDateTimeLabel``, ``span#addressLabel``,
``span#shopFullNameLabel``, ``span#totalAmountLabel``, and a product table with
``Name`` / ``Quantity`` / ``Gross Unit Price`` columns.
"""

from datetime import datetime
from typing import NamedTuple

import pytest


class ReceiptExpectation(NamedTuple):
    """Bundle of expected parsed values for a given mock receipt HTML."""

    html: str
    date: datetime
    address: str
    shop_name: str
    total_price: float
    items: list[tuple[str, float, float]]


_MOCK_HTML = """<!DOCTYPE html>
<html>
  <body>
    <span id="sdcDateTimeLabel">20/01/2026 10:30:00 AM</span>
    <span id="addressLabel">  123 Main Street  </span>
    <span id="shopFullNameLabel">Test Shop</span>
    <span id="totalAmountLabel">25.50</span>
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Quantity</th>
          <th>Gross Unit Price</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>Apple</td><td>2.0</td><td>5.00</td></tr>
        <tr><td>Bread</td><td>1.0</td><td>15.50</td></tr>
      </tbody>
    </table>
  </body>
</html>
"""


@pytest.fixture
def mock_receipt() -> ReceiptExpectation:
    """Return a complete, internally consistent receipt mock and expected values.

    The line-item totals sum exactly to ``total_price`` (2*5.00 + 1*15.50 = 25.50)
    so ``CrawledDataStorage.validate()`` passes against this fixture.

    Returns:
        ReceiptExpectation: Mock HTML and the values the parsers should produce.

    """
    return ReceiptExpectation(
        html=_MOCK_HTML,
        date=datetime(2026, 1, 20, 10, 30, 0),
        address="123 Main Street",
        shop_name="Test Shop",
        total_price=25.50,
        items=[
            ("Apple", 2.0, 5.0),
            ("Bread", 1.0, 15.5),
        ],
    )


@pytest.fixture
def mock_receipt_html(mock_receipt: ReceiptExpectation) -> str:
    """Return only the raw mock HTML, for tests that don't need expected values.

    Args:
        mock_receipt (ReceiptExpectation): Full mock bundle.

    Returns:
        str: The mock receipt HTML.

    """
    return mock_receipt.html
