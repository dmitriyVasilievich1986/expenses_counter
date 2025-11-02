"""API v1 router module."""

__all__ = ("router",)

from fastapi import APIRouter

from .category.category import router as category_router
from .shop.shop import router as shop_router

router = APIRouter(prefix="/v1")

router.include_router(category_router)
router.include_router(shop_router)
