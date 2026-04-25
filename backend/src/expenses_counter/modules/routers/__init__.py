"""Routers module."""

from .api import router as api_router
from .system import router as system_router

__all__ = ("api_router", "system_router")
