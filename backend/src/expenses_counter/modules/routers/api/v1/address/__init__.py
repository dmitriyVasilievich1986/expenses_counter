"""Address router module."""

__all__ = ("router",)

from fastapi import APIRouter

from .admin_only import router as admin_only_router
from .all_users import router as all_users_router

router = APIRouter(tags=["Address"])

router.include_router(all_users_router)
router.include_router(admin_only_router)
