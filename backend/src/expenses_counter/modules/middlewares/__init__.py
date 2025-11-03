"""Middlewares module."""

from .app_lifespan import lifespan
from .dependencies import get_address, get_category, get_config, get_db, get_shop

__all__ = (
    "get_address",
    "get_category",
    "get_config",
    "get_db",
    "get_shop",
    "lifespan",
)
