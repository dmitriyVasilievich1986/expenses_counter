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

    def __str__(self) -> str:
        """Return a human-readable summary of metadata and the line-item table.

        Returns:
            str: Concatenation of the HTML metadata block and the table string.

        """
        payload = self.html_parser.__str__()
        payload += "\n" + self.df.__str__()

        return payload
