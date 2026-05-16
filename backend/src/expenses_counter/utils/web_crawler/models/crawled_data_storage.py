"""Aggregate receipt HTML into metadata parsing and tabular line-item data."""

from .html_parser import HTMLParser
from .table_parser import TableParser


class CrawledDataStorage:
    """Bundle raw receipt HTML with parsers for metadata and product rows."""

    def __init__(self, html: str) -> None:
        """Initialize parsers for the given receipt HTML.

        Args:
            html (str): Raw HTML of the receipt page or fragment.

        """
        self.html = html
        self.html_parser = HTMLParser(html=html)
        self.df = TableParser(html=html)

    def validate(self) -> None:
        """Assert the crawl produced usable data and totals agree.

        Requires a non-empty line-item table, date, street address, and
        total from the HTML parser, and checks that the parser total matches
        the sum of per-line ``total`` values within one currency unit.

        Returns:
            None

        Raises:
            ValueError: If the table is empty, if date, address, or total is
                missing from the HTML, or if the HTML total and table sum
                differ by more than 1.

        """
        if self.df.empty:
            raise ValueError("Table parser is empty")
        if self.html_parser.date is None:
            raise ValueError("Date is not found")
        if self.html_parser.street_address is None:
            raise ValueError("Address is not found")
        if self.html_parser.total_price is None:
            raise ValueError("Total price is not found")

        if abs(self.html_parser.total_price - self.df.sum(axis=0)["total"]) > 1:
            raise ValueError("Total price does not match the sum of the table")

    def __str__(self) -> str:
        """Return a human-readable summary of metadata and the line-item table.

        Returns:
            str: Concatenation of the HTML metadata block and the table string.

        """
        payload = self.html_parser.__str__()
        payload += "\n" + self.df.__str__()

        return payload
