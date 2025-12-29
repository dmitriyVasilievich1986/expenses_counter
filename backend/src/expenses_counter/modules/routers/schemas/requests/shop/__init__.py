"""Shop request schemas module."""

from .get_all_shops_query import GetAllShopsQuery
from .post_shop_body import PostShopBody
from .put_shop_body import PutShopBody

__all__ = ("GetAllShopsQuery", "PostShopBody", "PutShopBody")
