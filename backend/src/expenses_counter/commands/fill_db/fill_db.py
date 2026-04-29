"""CLI command that seeds the database with a minimal sample expense graph."""

__all__ = ("FillDBCommand",)


from datetime import date

from expenses_counter.config import AppConfig
from expenses_counter.modules.routers.schemas.requests.address import PostAddressBody
from expenses_counter.modules.routers.schemas.requests.category import PostCategoryBody
from expenses_counter.modules.routers.schemas.requests.product import PostProductBody
from expenses_counter.modules.routers.schemas.requests.shop import PostShopBody
from expenses_counter.modules.routers.schemas.requests.transaction import PostTransactionBody
from expenses_counter.services.daos import AddressDAO, CategoryDAO, ProductDAO, ShopDAO, TransactionDAO
from expenses_counter.services.database import AsyncDatabaseClient

from ..base import BaseCommand


class FillDBCommand(BaseCommand):
    """Populate the database with one linked category, shop, address, product, and transaction."""

    def __init__(
        self,
        app_config: AppConfig | None = None,
        db_client: AsyncDatabaseClient | None = None,
    ) -> None:
        """Configure paths and clients used when validating and executing the command.

        Args:
            app_config (AppConfig | None, optional): Application configuration.
                Defaults to ``AppConfig.get_or_create()``.
            db_client (AsyncDatabaseClient | None, optional): Database client for DAOs.
                Defaults to a new client built from ``app_config``.

        """
        self.app_config = app_config or AppConfig.get_or_create()
        self.db_client = db_client or AsyncDatabaseClient(self.app_config)

    async def initialize(self) -> None:
        """Prepare the command. No async setup is required for this implementation.

        Returns:
            None

        """
        pass

    async def validate(self) -> None:
        """Validate the command. No validation is required for this implementation.

        Returns:
            None

        """
        pass

    async def execute(self) -> None:
        """Create a single sample category, shop, address, product, and transaction.

        Returns:
            None

        """
        category = await CategoryDAO(self.db_client).create(
            **PostCategoryBody(name="Category 1").model_dump(),
        )
        shop = await ShopDAO(self.db_client).create(
            **PostShopBody(name="Shop 1", category_id=category.id).model_dump(),
        )
        address = await AddressDAO(self.db_client).create(
            **PostAddressBody(local_name="Local name 1", address="Address 1", shop_id=shop.id).model_dump(),
        )
        product = await ProductDAO(self.db_client).create(
            **PostProductBody(name="Product 1", category_id=category.id).model_dump(),
        )
        await TransactionDAO(self.db_client).create(
            **PostTransactionBody(
                product_id=product.id,
                address_id=address.id,
                count=1,
                price=100,
                date=date.today(),
            ).model_dump(),
        )
