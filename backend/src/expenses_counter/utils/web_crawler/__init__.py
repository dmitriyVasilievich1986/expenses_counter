"""Web crawler utils module."""

from .crawler import Crawler
from .html_parser import HTMLParser
from .table_parser import TableParser

__all__ = ("Crawler", "HTMLParser", "TableParser")
