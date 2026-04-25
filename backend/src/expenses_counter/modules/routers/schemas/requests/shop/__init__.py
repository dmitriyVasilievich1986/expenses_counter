"""Shop request schemas module."""

from .get_all_shops_query import GetAllShopsQuery
from .patch_shop_body import PatchShopBody
from .post_shop_body import PostShopBody
from .put_shop_body import PutShopBody

__all__ = ("GetAllShopsQuery", "PatchShopBody", "PostShopBody", "PutShopBody")
