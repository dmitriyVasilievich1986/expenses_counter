"""Base DAO module."""

from .base_dao import BaseDAO
from .error_handler import error_handler
from .exceptions import DBException, NotFoundException, RelationshipNotFoundException

__all__ = ("BaseDAO", "DBException", "NotFoundException", "RelationshipNotFoundException", "error_handler")
