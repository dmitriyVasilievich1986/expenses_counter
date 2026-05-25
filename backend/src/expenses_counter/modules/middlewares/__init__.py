"""Middlewares module."""

__all__ = (
    "get_config",
    "get_db",
    "lifespan",
)

from .app_lifespan import lifespan
from .dependencies import get_config, get_db
