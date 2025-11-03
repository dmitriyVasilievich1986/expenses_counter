"""Product schemas module."""

from .get import ProductGet
from .patch import ProductPatch
from .post import ProductPost
from .put import ProductPut

__all__ = ("ProductGet", "ProductPatch", "ProductPost", "ProductPut")
