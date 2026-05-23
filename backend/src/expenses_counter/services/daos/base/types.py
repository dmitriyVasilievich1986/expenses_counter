"""Types for the base DAO."""

__all__ = ("FilterType",)

from typing import Any

from sqlalchemy.sql import ColumnElement

FilterType = list[ColumnElement[bool]] | list[ColumnElement[bool] | dict[str, Any]] | None
