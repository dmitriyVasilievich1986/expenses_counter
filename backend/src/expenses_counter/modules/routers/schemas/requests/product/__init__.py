"""Product request schemas module."""

from .get_all_products_query import GetAllProductsQuery
from .patch_product_body import PatchProductBody
from .post_product_body import PostProductBody
from .put_product_body import PutProductBody

__all__ = ("GetAllProductsQuery", "PatchProductBody", "PostProductBody", "PutProductBody")
