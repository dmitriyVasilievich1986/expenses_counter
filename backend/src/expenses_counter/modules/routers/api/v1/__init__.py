"""API v1 router module."""

__all__ = ("router",)

from fastapi import APIRouter

from .address import router as address_router
from .category import router as category_router
from .product import router as product_router
from .shop import router as shop_router
from .statistics import router as statistics_router
from .transaction import router as transaction_router

router = APIRouter(prefix="/v1")

router.include_router(category_router)
router.include_router(product_router)
router.include_router(address_router)
router.include_router(shop_router)
router.include_router(transaction_router)
router.include_router(statistics_router)
