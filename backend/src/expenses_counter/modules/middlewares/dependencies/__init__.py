"""Dependencies module."""

from .daos import get_category, get_shop
from .get_config import get_config
from .get_db import get_db

__all__ = ("get_category", "get_config", "get_db", "get_shop")
