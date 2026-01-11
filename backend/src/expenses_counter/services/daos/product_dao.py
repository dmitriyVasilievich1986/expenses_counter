"""Product DAO module."""

__all__ = ("ProductDAO",)

from expenses_counter.services.daos.base import BaseDAO
from expenses_counter.services.database.models.product import Product


class ProductDAO(BaseDAO[Product]):
    """Data Access Object for Product entities.

    This DAO implements CRUD operations for Product entities, interacting with
    the database through the provided database client. It extends BaseDAO with
    product-specific implementations.
    """

    database_model = Product
    get_all_columns = (Product.id, Product.name, Product.description, Product.category_id)
    select_in_options_single = (Product.category,)
