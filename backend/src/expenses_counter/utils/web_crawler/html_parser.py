"""HTML parser for extracting transaction metadata from receipt HTML."""

__all__ = ("HTMLParser",)

import re
from datetime import datetime

from bs4 import BeautifulSoup

from .table_parser import TableParser


class HTMLParser:
    """Parser for extracting date and address information from receipt HTML.

    This parser uses BeautifulSoup to extract transaction metadata from
    HTML receipts, specifically targeting date/time and shop address information.
    Results are cached after first access for performance.

    Attributes:
        html: Raw HTML string to parse
        bs: BeautifulSoup object for HTML parsing

    """

    _date: datetime | None = None
    _address: str | None = None
    _shop_name: str | None = None
    _total_price: float | None = None

    def __init__(self, html: str) -> None:
        """Initialize HTMLParser with receipt HTML content.

        Args:
            html: Raw HTML string from receipt page

        """
        self.html = html
        self.bs = BeautifulSoup(self.html, "lxml")

    @property
    def date(self) -> datetime:
        """Extract and parse transaction date from receipt HTML.

        Looks for a span element with id "sdcDateTimeLabel" and parses its content
        as a datetime in Serbian format (DD.MM.YYYY.HH:MM:SS). The result is cached
        after first access.

        Returns:
            Datetime object representing the transaction date and time

        Raises:
            ValueError: If the date span element is not found in the HTML

        Example:
            >>> parser = HTMLParser(html_content)
            >>> parser.date
            datetime.datetime(2026, 1, 17, 14, 30, 45)

        """
        if self._date is not None:
            return self._date

        date_span = self.bs.find("span", id="sdcDateTimeLabel")
        if date_span is None:
            raise ValueError("Date span not found")
        date_reg = re.sub(r"\s+", "", date_span.contents[0])
        self._date = datetime.strptime(date_reg, "%d.%m.%Y.%H:%M:%S")
        return self._date

    @property
    def address(self) -> str:
        """Extract shop address from receipt HTML.

        Looks for a span element with id "addressLabel" and returns its text
        content as the shop address. The result is cached after first access.

        Returns:
            String containing the shop's address

        Raises:
            ValueError: If the address span element is not found in the HTML

        Example:
            >>> parser = HTMLParser(html_content)
            >>> parser.address
            'Beograd, Jurija Gagarina 146'

        """
        if self._address is not None:
            return self._address

        address_span = self.bs.find("span", id="addressLabel")
        if address_span is None:
            raise ValueError("Address span not found")

        self._address = str(address_span.text).strip()
        return self._address

    @property
    def shop_name(self) -> str:
        """Extract shop name from receipt HTML.

        Looks for a span element with id "shopFullNameLabel" and returns its text
        content as the shop's full name. The result is cached after first access.

        Returns:
            String containing the shop's full name

        Raises:
            ValueError: If the shop name span element is not found in the HTML

        Example:
            >>> parser = HTMLParser(html_content)
            >>> parser.shop_name
            'MAXI D.O.O. BEOGRAD'

        """
        if self._shop_name is not None:
            return self._shop_name

        shop_name_span = self.bs.find("span", id="shopFullNameLabel")
        if shop_name_span is None:
            raise ValueError("Shop name span not found")

        self._shop_name = str(shop_name_span.text).strip()
        return self._shop_name

    @property
    def total_price(self) -> float:
        """Extract total price from receipt HTML.

        Looks for a span element with id "totalAmountLabel" and returns its text
        content as the total price. The result is cached after first access.

        Returns:
            Float containing the total price

        """
        if self._total_price is not None:
            return self._total_price

        total_price_span = self.bs.find("span", id="totalAmountLabel")
        if total_price_span is None:
            raise ValueError("Total price span not found")

        self._total_price = TableParser.convert_float(total_price_span.text.strip())
        return self._total_price
