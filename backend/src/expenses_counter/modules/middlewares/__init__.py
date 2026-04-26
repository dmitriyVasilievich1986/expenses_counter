"""Middlewares module."""

__all__ = (
    "get_address",
    "get_category",
    "get_config",
    "get_db",
    "get_product",
    "get_shop",
    "get_transaction",
    "lifespan",
)

from .app_lifespan import lifespan
from .dependencies import get_address, get_category, get_config, get_db, get_product, get_shop, get_transaction
