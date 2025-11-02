"""Database services module."""

from sqlalchemy.orm import declarative_base

from .client import DatabaseClient

Base = declarative_base()

__all__ = ("Base", "DatabaseClient")
