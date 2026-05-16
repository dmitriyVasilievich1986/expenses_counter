"""HTML parser for extracting transaction metadata from receipt HTML."""

__all__ = ("HTMLParser",)

import re
from datetime import datetime

from bs4 import BeautifulSoup

from .table_parser import TableParser


class HTMLParser:
    """Parse receipt HTML and expose date, address, shop name, and total."""

    _date: datetime | None = None
    _address: str | None = None
    _shop_name: str | None = None
    _total_price: float | None = None

    def __init__(self, html: str) -> None:
        """Parse the given HTML with BeautifulSoup.

        Args:
            html (str): Raw receipt HTML.

        """
        self.html = html
        self.bs = BeautifulSoup(self.html, "lxml")

    def __str__(self) -> str:
        """Return a multi-line summary of parsed receipt metadata.

        Returns:
            str: Lines for date, address, shop name, and total price.

        """
        payload = f"Date: {self.date}"
        payload += f"\nAddress: {self.street_address}"
        payload += f"\nShop name: {self.shop_name}"
        payload += f"\nTotal price: {self.total_price}"

        return payload

    @property
    def date(self) -> datetime:
        """Return the receipt date and time from ``span#sdcDateTimeLabel``.

        Returns:
            datetime: Parsed receipt timestamp.

        Raises:
            ValueError: If the date span is missing from the HTML.

        """
        if self._date is not None:
            return self._date

        date_span = self.bs.find("span", id="sdcDateTimeLabel")
        if date_span is None:
            raise ValueError("Date span not found")

        date_reg = re.sub(r"\s+", "", str(date_span.contents[0]))
        self._date = datetime.strptime(date_reg, "%m/%d/%Y%H:%M:%S%p")

        return self._date

    @property
    def street_address(self) -> str:
        """Return the street address from ``span#addressLabel``.

        Returns:
            str: Trimmed address text.

        Raises:
            ValueError: If the address span is missing from the HTML.

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
        """Return the shop display name from ``span#shopFullNameLabel``.

        Returns:
            str: Trimmed shop name.

        Raises:
            ValueError: If the shop name span is missing from the HTML.

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
        """Return the total amount from ``span#totalAmountLabel``.

        Returns:
            float: Parsed total using the same rules as ``TableParser``.

        Raises:
            ValueError: If the total amount span is missing from the HTML.

        """
        if self._total_price is not None:
            return self._total_price

        total_price_span = self.bs.find("span", id="totalAmountLabel")
        if total_price_span is None:
            raise ValueError("Total price span not found")

        self._total_price = TableParser.convert_float(str(total_price_span.text).strip())
        return self._total_price
