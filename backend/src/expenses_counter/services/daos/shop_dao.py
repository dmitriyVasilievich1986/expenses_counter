"""Shop DAO module."""

__all__ = ("ShopDAO",)

from expenses_counter.services.daos.base import BaseDAO
from expenses_counter.services.database.models.shop import Shop


class ShopDAO(BaseDAO[Shop]):
    """Data Access Object for Shop entities.

    This DAO implements CRUD operations for Shop entities, interacting with
    the database through the provided database client. It extends BaseDAO with
    shop-specific implementations.
    """

    database_model = Shop
    get_all_columns = (Shop.id, Shop.name, Shop.description, Shop.icon, Shop.category_id)
    select_in_options_single = (Shop.category, Shop.addresses)
