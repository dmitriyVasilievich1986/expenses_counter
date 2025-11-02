from fastapi import APIRouter

from .health import router as health_router
from .version import router as version_router

__all__ = ("router",)

router = APIRouter(prefix="/system", tags=["System"])

router.include_router(version_router)
router.include_router(health_router)
