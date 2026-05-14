"""System router module."""

__all__ = ("router",)

from fastapi import APIRouter

from .health import router as health_router
from .index import router as index_router
from .login import router as login_router
from .me import router as me_router
from .version import router as version_router

router = APIRouter(prefix="/api", tags=["System"])

router.include_router(version_router)
router.include_router(health_router)
router.include_router(login_router)
router.include_router(me_router)

router.include_router(index_router)
