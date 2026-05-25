"""Dependencies module."""

__all__ = (
    "get_config",
    "get_db",
    "user_authorized",
)

from .get_config import get_config
from .get_db import get_db
from .user_authorized import user_authorized
