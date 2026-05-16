"""Command for crawling receipt URL and creating transaction records."""

__all__ = ("CreateTransactionsFromCrawledDataCommand",)


from typing import Any, TYPE_CHECKING

from loguru import logger
from sqlalchemy.exc import NoResultFound

from expenses_counter.commands.base import BaseCommand
from expenses_counter.config import AppConfig
from expenses_counter.services.daos import AddressDAO, ProductDAO, TransactionDAO
from expenses_counter.services.database import AsyncDatabaseClient

if TYPE_CHECKING:
    from expenses_counter.services.database.models import Address, User
    from expenses_counter.utils.web_crawler import CrawledDataStorage


class CreateTransactionsFromCrawledDataCommand(BaseCommand):
    """Persist crawled receipt line items as products and transactions for a user.

    After `validate`, `address` and `category_id` are set from the parsed shop name.

    Attributes:
        address (Address | None): Target store address resolved from crawled shop name,
            set during `validate`. Initially ``None``.
        category_id (int): Shop category id used when creating missing products,
            set during `validate` from the resolved address's shop.

    """

    address: "Address | None" = None
    category_id: int

    def __init__(
        self,
        data: "CrawledDataStorage",
        user: "User",
        db: AsyncDatabaseClient | None = None,
    ) -> None:
        """Create a command bound to crawled receipt data and a user.

        Args:
            data (CrawledDataStorage): Parsed receipt content (HTML and tabular rows).
            user (User): Owner for created transactions.
            db (AsyncDatabaseClient | optional): Async database client. If ``None``,
                `initialize` creates one from application config.

        Returns:
            None:

        """
        self.data = data
        self.user = user
        self.db = db

    async def initialize(self, **_: Any) -> None:
        """Ensure a database client exists and log startup context.

        Args:
            **_ (Any): Ignored keyword arguments kept for ``BaseCommand`` compatibility.

        Returns:
            None:

        """
        if self.db is None:
            app_config = AppConfig.get_or_create()
            self.db = AsyncDatabaseClient(app_config=app_config)

        logger.info(f"Initialized command with user {self.user.id}")

    async def validate(self) -> None:
        """Validate crawled data and resolve the shop address and category.

        Loads `address` by matching the parsed shop ``local_name`` and sets
        `category_id` from that address's shop when `address` was not preset.

        Returns:
            None:

        """
        self.data.validate()

        if self.address is None:
            address_dao = AddressDAO(database_client=self.db)  # type: ignore[arg-type]
            self.address = await address_dao.get_by_pk(self.data.html_parser.shop_name, "local_name")
            self.category_id = self.address.shop.category_id  # type: ignore[assignment]
        else:
            self.category_id = self.address.shop.category_id  # type: ignore[assignment]

        logger.info(f"Validated command with address {self.address.id} and category {self.category_id}")

    async def execute(self) -> None:
        """Insert one transaction per dataframe row using shared receipt metadata.

        Resolves each product by name under the crawl shop scope, creating the
        product with `category_id` when missing, then attaches quantity, unit
        price, and receipt date.

        Returns:
            None:

        """
        logger.info(f"Executed command with {len(self.data.df)} transactions")
        async with self.db.session_factory() as session:  # type: ignore[union-attr]
            transaction_dao = TransactionDAO(session=session, database_client=None, user=self.user)
            product_dao = ProductDAO(session=session, database_client=None)

            for _, row in self.data.df.iterrows():
                try:
                    product = await product_dao.get_by_name(self.data.html_parser.shop_name)
                except NoResultFound:
                    product = await product_dao.create(name=row["name"], category_id=self.category_id)

                await transaction_dao.create(
                    date=self.data.html_parser.date,
                    address_id=self.address.id,  # type: ignore[union-attr]
                    product_id=product.id,
                    count=row["quantity"],
                    price=row["unit_price"],
                    user_id=self.user.id,
                )

        logger.info(f"Completed command with data:\n{self.data}")
