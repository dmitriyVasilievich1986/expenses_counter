"""API v1 router module."""

__all__ = ("router",)

from fastapi import APIRouter

from .category import router as category_router
from .product import router as product_router

router = APIRouter(prefix="/v1")

router.include_router(category_router)
router.include_router(product_router)
