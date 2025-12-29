"""Product request schemas module."""

from .get_all_products_query import GetAllProductsQuery
from .post_product_body import PostProductBody
from .put_product_body import PutProductBody

__all__ = ("GetAllProductsQuery", "PostProductBody", "PutProductBody")
