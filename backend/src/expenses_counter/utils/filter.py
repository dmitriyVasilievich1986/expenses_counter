"""Pydantic filter model and conversion to SQLAlchemy ``WHERE`` clauses."""

__all__ = ("Filter",)

from datetime import date, datetime
from typing import Any, Literal, Self

from pydantic import BaseModel, Field, model_validator
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import ColumnElement


class Filter[ColumnType: str](BaseModel):
    """Declarative filter triple for paginated or filtered list APIs.

    ``ColumnType`` is typically a string literal union of allowed ORM attribute
    names. Supported operators: null checks (``isnull``, ``notnull``),
    comparisons (``eq``, ``ge``, ``gt``, ``le``, ``lt``), membership (``in``),
    and substring match (``like``, ``ilike``).

    """

    column: ColumnType = Field(..., description="The column to filter by")
    operator: Literal["isnull", "notnull", "eq", "ge", "gt", "le", "lt", "in", "like", "ilike"] = Field(
        ..., description="The operator to use for the filter"
    )
    value: str | int | list[str | int] | float | date | None = Field(..., description="The value to filter by")

    @model_validator(mode="after")
    def coerce_iso_date_strings_for_comparison(self) -> Self:
        """Coerce ISO date strings to ``date`` for numeric-style operators.

        Strings matching ``%Y-%m-%d`` become ``date`` objects for ``eq``, ``ge``,
        ``gt``, ``le``, ``lt``, and ``in``. ``like``, ``ilike``, ``isnull``, and
        ``notnull`` leave ``value`` unchanged so patterns and null semantics stay
        intact. Non-matching strings are unchanged.

        Returns:
            Self: Model copy with coerced ``value``, or ``self`` when no change
                applies.
        """
        if self.operator in ("like", "ilike", "isnull", "notnull"):
            return self

        if isinstance(self.value, str):
            try:
                parsed = datetime.strptime(self.value, "%Y-%m-%d").date()
                return self.model_copy(update={"value": parsed})
            except ValueError:
                return self

        return self

    def to_sqlalchemy_filter(self, cls: type[DeclarativeBase]) -> ColumnElement[bool]:
        """Return a boolean SQLAlchemy expression for this filter.

        ``isnull`` and ``notnull`` ignore ``value``. ``like`` and ``ilike``
        surround ``value`` with ``%`` for substring match.

        Args:
            cls (type[DeclarativeBase]): Declarative model that defines the
                attribute named by ``column``.

        Returns:
            ColumnElement[bool]: Predicate suitable for ``Query.where()`` or
                ``filter()``.

        Raises:
            ValueError: If ``operator`` is not one of the supported literals
                (unexpected after successful Pydantic validation).

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
            case "in":
                return column.in_(self.value)
            case "like":
                return column.like(f"%{self.value}%")
            case "ilike":
                return column.ilike(f"%{self.value}%")
            case _:
                raise ValueError(f"Invalid operator: {self.operator}")
