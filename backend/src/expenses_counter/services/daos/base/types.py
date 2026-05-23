"""Types for the base DAO."""

__all__ = ("AcceptableFiltersType",)

from typing import Any

from sqlalchemy.sql import ColumnElement

from expenses_counter.utils.filter import Filter

AcceptableFiltersType = list[ColumnElement[bool]] | list[dict[str, Any]] | list[Filter[str]] | None
