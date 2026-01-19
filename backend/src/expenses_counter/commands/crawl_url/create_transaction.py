"""Command for creating transaction from parsed receipt data."""

__all__ = ("CreateTransactionCommand",)

from loguru import logger

from expenses_counter.commands.base import BaseCommand
from expenses_counter.config import AppConfig
from expenses_counter.services.daos import AddressDAO, CategoryDAO, ProductDAO, TransactionDAO
from expenses_counter.services.database import AsyncDatabaseClient
from expenses_counter.services.database.models import Address, Category, Product
from expenses_counter.utils.web_crawler import HTMLParser, TableParser


class CreateTransactionCommand(BaseCommand):
    """Command to create transaction records from parsed receipt data.

    This command processes parsed receipt data (metadata and product table) and
    creates corresponding transaction records in the database. It handles product
    lookup/creation, address validation, and category assignment.

    Attributes:
        html_parser: Parser containing receipt metadata (date and address)
        table_parser: Parser containing product table data
        default_category_id: Optional default category ID for new products
        app_config: Application configuration (set during initialization)
        db_client: Async database client (set during initialization)

    """

    app_config: AppConfig
    db_client: AsyncDatabaseClient

    def __init__(
        self, html_parser: HTMLParser, table_parser: TableParser, default_category_id: int | None = None
    ) -> None:
        """Initialize CreateTransactionCommand with parsed receipt data.

        Args:
            html_parser: HTMLParser instance with receipt HTML
            table_parser: TableParser instance with product table data
            default_category_id: Optional category ID for new products. If None,
                uses the first available category from the database.

        """
        self.html_parser = html_parser
        self.table_parser = table_parser
        self.default_category_id = default_category_id

    async def initialize(self) -> None:
        """Initialize command resources.

        Sets up the application configuration and async database client
        required for transaction creation.

        """
        self.app_config = AppConfig.get_or_create()
        self.db_client = AsyncDatabaseClient(app_config=self.app_config)

    async def _get_category(self, category_id: int | None = None) -> Category:
        """Get category by ID or return the first available category.

        Args:
            category_id: Optional category ID to retrieve

        Returns:
            Category object matching the ID, or the first available category
            if ID is None or not found

        Raises:
            ValueError: If no categories exist in the database

        """
        category_dao = CategoryDAO(database_client=self.db_client)
        if not category_id or (category := await category_dao.get_by_id(category_id)) is None:
            all_categories = await category_dao.get_all()
            if len(all_categories) == 0:
                raise ValueError("No categories found")
            category = all_categories[0]

        logger.debug(f"Using category: {category.id}, name: {category.full_name}")
        return category

    async def _get_or_create_product(self, name: str) -> Product:
        """Get existing product by name or create a new one.

        Args:
            name: Product name to look up or create

        Returns:
            Product object, either existing or newly created

        Note:
            New products are created with the default_category_id specified
            during command initialization.

        """
        product_dao = ProductDAO(database_client=self.db_client)
        if (product := await product_dao.get_by_name(name)) is None:
            product = await product_dao.create(name=name, category_id=self.default_category_id)

        return product

    async def _get_address(self, address: str) -> Address:
        """Get address by address string.

        Args:
            address: Address string to look up

        Returns:
            Address object matching the provided address string

        Raises:
            ValueError: If the address is not found in the database

        """
        address_dao = AddressDAO(database_client=self.db_client)
        if (address := await address_dao.get_by_address(address)) is None:
            raise ValueError("Address not found")

        return address

    async def execute(self) -> None:
        """Execute transaction creation from parsed receipt data.

        This method:
        1. Retrieves the address from the database
        2. Iterates through each product row in the table parser
        3. Gets or creates each product
        4. Creates a transaction record for each product with quantity and price

        Raises:
            ValueError: If the address is not found in the database
            Exception: For any database operation errors

        """
        address = await self._get_address(self.html_parser.address)
        transaction_dao = TransactionDAO(database_client=self.db_client)

        for i, row in self.table_parser.iterrows():
            logger.info(f"Processing row {i + 1} of {len(self.table_parser)}")
            product = await self._get_or_create_product(row["name"])
            await transaction_dao.create(
                date=self.html_parser.date,
                product_id=product.id,
                address_id=address.id,
                count=row["quantity"],
                price=row["unit_price"],
            )

    async def validate(self) -> None:
        """Validate parsed receipt data before transaction creation.

        Performs four validation checks:
        1. Verifies table parser contains product data (not empty)
        2. Validates date can be extracted from HTML parser
        3. Validates address can be extracted from HTML parser
        4. Validates default category exists or retrieves first available category

        All validation errors are logged before raising exceptions.

        Raises:
            ValueError: If table parser is empty, date/address cannot be parsed,
                or no categories are found in the database
            Exception: For any unexpected errors during validation

        """
        if self.table_parser.empty:
            logger.error("Table parser is empty")
            raise ValueError("Table parser is empty")

        try:
            _ = self.html_parser.date
        except ValueError as e:
            logger.error(f"Error parsing date: {e}")
            raise ValueError("HTML parser is empty") from e
        except Exception as e:
            logger.error(f"Error parsing date: {e}")
            raise e

        try:
            _ = self.html_parser.address
        except ValueError as e:
            logger.error(f"Error parsing address: {e}")
            raise ValueError("HTML parser is empty") from e
        except Exception as e:
            logger.error(f"Error parsing address: {e}")
            raise e

        try:
            category = await self._get_category(self.default_category_id)
            self.default_category = category.id
        except ValueError as e:
            logger.error(f"Error getting category: {e}")
            raise ValueError("Default category not found") from e
        except Exception as e:
            logger.error(f"Error getting category: {e}")
            raise e
