"""Query filter model and helpers to build SQLAlchemy boolean expressions."""

__all__ = ("Filter",)

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import ColumnElement


class Filter[ColumnType: str](BaseModel):
    """One declarative filter (column, operator, value) for list endpoints.

    Operators include null checks, comparisons, and case-sensitive or
    case-insensitive substring match.
    """

    column: ColumnType = Field(..., description="The column to filter by")
    operator: Literal["isnull", "notnull", "eq", "ge", "gt", "le", "lt", "like", "ilike"] = Field(
        ..., description="The operator to use for the filter"
    )
    value: str | int | None | datetime | date | float = Field(..., description="The value to filter by")

    def to_sqlalchemy_filter(self, cls: type[DeclarativeBase]) -> ColumnElement[bool]:
        """Build a SQL expression that applies this filter to ``cls``.

        ``isnull`` and ``notnull`` only test the column against SQL NULL;
        ``value`` is not used in the expression. For ``like`` and ``ilike``,
        ``value`` is wrapped with ``%`` on both sides for substring matching.

        Args:
            cls (type[DeclarativeBase]): Declarative ORM model exposing the
                attribute named by ``column``.

        Returns:
            ColumnElement[bool]: Boolean SQL expression for ``where()`` /
                ``filter()``.

        Raises:
            ValueError: If ``operator`` is not a supported literal (should not
                occur when the model is validated).

        """
        column: ColumnElement[Any] = getattr(cls, self.column)

        match self.operator:
            case "isnull":
                return column.is_(None)
            case "notnull":
                return column.isnot(None)
            case "eq":
                return column == self.value
            case "ge":
                return column >= self.value
            case "gt":
                return column > self.value
            case "le":
                return column <= self.value
            case "lt":
                return column < self.value
            case "like":
                return column.like(f"%{self.value}%")
            case "ilike":
                return column.ilike(f"%{self.value}%")
            case _:
                raise ValueError(f"Invalid operator: {self.operator}")
