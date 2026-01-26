"""Command for crawling receipt URL and creating transaction records."""

__all__ = ("CrawlAndCreateCommand",)


from expenses_counter.commands.base import BaseCommand
from expenses_counter.utils.web_crawler import Crawler, HTMLParser, TableParser

from .create_transaction import CreateTransactionCommand


class CrawlAndCreateCommand(BaseCommand):
    """Command to crawl a receipt URL and create transaction records.

    This command orchestrates the complete workflow of:
    1. Crawling a receipt URL using Selenium
    2. Parsing the HTML to extract transaction metadata
    3. Parsing product table data
    4. Creating transaction records in the database

    Attributes:
        url: Receipt URL to crawl
        default_category_id: Optional default category ID for products

    """

    def __init__(self, url: str, default_category_id: int | None = None) -> None:
        """Initialize CrawlAndCreateCommand with URL and optional category.

        Args:
            url: Receipt URL to crawl and process
            default_category_id: Optional category ID to use for new products.
                If None, will use the first available category.

        """
        self.url = url
        self.default_category_id = default_category_id

    async def initialize(self) -> None:
        """Initialize command resources.

        This command does not require initialization as it delegates to
        CreateTransactionCommand which handles its own initialization.

        """
        pass

    async def validate(self) -> None:
        """Validate command preconditions.

        This command does not perform validation at this level as validation
        is delegated to CreateTransactionCommand which validates the parsed data.

        """
        pass

    async def execute(self) -> None:
        """Execute the complete crawl and create workflow.

        This method orchestrates the following steps:
        1. Creates a Crawler instance and fetches HTML from the URL
        2. Parses the HTML to extract transaction metadata (date, address)
        3. Parses the product table data
        4. Creates a CreateTransactionCommand with parsed data
        5. Initializes, validates, and executes the transaction creation

        Raises:
            ValueError: If URL crawling fails, parsing fails, or transaction
                creation validation fails
            selenium.common.exceptions.WebDriverException: If browser automation fails
            Exception: For any unexpected errors during the process

        Example:
            >>> command = CrawlAndCreateCommand(
            ...     url="https://receipt.example.com/12345",
            ...     default_category_id=1
            ... )
            >>> await command.initialize()
            >>> await command.validate()
            >>> await command.execute()

        """
        crawler = Crawler(url=self.url)
        html = crawler.run()
        html_parser = HTMLParser(html=html)
        table_parser = TableParser(html=html)
        create_transaction_command = CreateTransactionCommand(
            html_parser=html_parser, table_parser=table_parser, default_category_id=self.default_category_id
        )
        await create_transaction_command.initialize()
        await create_transaction_command.validate()
        await create_transaction_command.execute()
