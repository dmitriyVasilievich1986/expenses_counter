"""API v1 router module."""

__all__ = ("router",)

from fastapi import APIRouter

from .address.address import router as address_router
from .category.category import router as category_router
from .product.product import router as product_router
from .shop.shop import router as shop_router

router = APIRouter(prefix="/v1")

router.include_router(category_router)
router.include_router(shop_router)
router.include_router(address_router)
router.include_router(product_router)
