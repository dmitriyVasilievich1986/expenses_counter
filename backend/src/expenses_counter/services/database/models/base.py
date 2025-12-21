"""Base model module."""

__all__ = ("Base",)

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base model class for all SQLAlchemy models."""

    pass
