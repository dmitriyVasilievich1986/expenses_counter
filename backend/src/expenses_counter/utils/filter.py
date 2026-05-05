"""Query filter model and conversion to SQLAlchemy WHERE clauses."""

__all__ = ("Filter",)

from typing import Literal

from pydantic import BaseModel, Field
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import ColumnElement


class Filter[ColumnType: str](BaseModel):
    """Single column filter with operator and value for paginated list queries."""

    column: ColumnType = Field(..., description="The column to filter by")
    operator: Literal["eq", "like", "ilike"] = Field(..., description="The operator to use for the filter")
    value: str = Field(..., description="The value to filter by")

    def to_sqlalchemy_filter(self, cls: type[DeclarativeBase]) -> ColumnElement[bool]:
        """Return a SQLAlchemy boolean expression for this filter on ``cls``.

        For ``like`` and ``ilike``, the value is wrapped with ``%`` on both sides
        so the API passes a plain substring.

        Args:
            cls (type[DeclarativeBase]): Declarative ORM model whose attributes
                include the named ``column``.

        Returns:
            ColumnElement[bool]: Expression usable in ``where()`` / ``filter()``.

        Raises:
            ValueError: If ``operator`` is not a supported literal (should not
                occur when the model is validated).

        """
        match self.operator:
            case "eq":
                return getattr(cls, self.column) == self.value
            case "like":
                return getattr(cls, self.column).like(f"%{self.value}%")
            case "ilike":
                return getattr(cls, self.column).ilike(f"%{self.value}%")
            case _:
                raise ValueError(f"Invalid operator: {self.operator}")
