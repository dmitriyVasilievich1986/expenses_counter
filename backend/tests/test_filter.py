"""Unit tests for the Filter model in expenses_counter.utils.filter.

Note on the date-coercion validator:

The ``coerce_iso_date_strings_for_comparison`` validator returns a *new* model via
``self.model_copy(update={"value": parsed})``. Pydantic v2 supports a non-``self``
return only for the ``model_validate``/``model_validate_json`` paths; when
constructing via ``__init__`` Pydantic emits a UserWarning and the returned copy
is discarded, so the original string value survives.

These tests document the *current* behavior of both paths:
- ``Filter(...)``           -> string is NOT coerced
- ``Filter.model_validate`` -> string IS coerced to ``date``

In production, dict filters from the API arrive through
``Filter.model_validate`` (see ``base_dao.py``), so the coercion path covered
by the real flow does work.
"""

__all__ = ()

import warnings
from datetime import date
from typing import Literal

import pytest
from sqlalchemy.sql import ColumnElement
from sqlalchemy.sql.elements import BinaryExpression

from expenses_counter.services.database.models.category import Category
from expenses_counter.services.database.models.transaction import Transaction
from expenses_counter.utils.filter import Filter


def _compile(expr: ColumnElement[bool]) -> str:
    """Render a SQLAlchemy expression with bound values inlined for assertions."""
    return str(expr.compile(compile_kwargs={"literal_binds": True}))


CategoryFilter = Filter[Literal["name", "description", "parent_id", "id"]]
TransactionFilter = Filter[Literal["date", "price", "count", "product_id", "address_id", "id"]]


class TestDateCoercionViaInit:
    """Direct ``Filter(...)`` construction does not coerce date strings (current behavior)."""

    @pytest.mark.parametrize("operator", ["eq", "ge", "gt", "le", "lt"])
    def test_iso_date_string_is_not_coerced_via_init(self, operator: str):
        """Pydantic discards the validator's ``model_copy`` return when called via ``__init__``."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            f = TransactionFilter(column="date", operator=operator, value="2025-01-15")
        assert f.value == "2025-01-15"
        assert isinstance(f.value, str)

    @pytest.mark.parametrize("operator", ["like", "ilike"])
    def test_pattern_operators_keep_string_via_init(self, operator: str):
        """Pattern operators short-circuit before the date parse, so no warning is emitted."""
        f = CategoryFilter(column="name", operator=operator, value="2025-01-15")
        assert f.value == "2025-01-15"
        assert isinstance(f.value, str)

    @pytest.mark.parametrize("operator", ["isnull", "notnull"])
    def test_null_operators_do_not_touch_value_via_init(self, operator: str):
        """Null-check operators ignore the value and leave it unchanged."""
        f = CategoryFilter(column="parent_id", operator=operator, value="2025-01-15")
        assert f.value == "2025-01-15"


class TestDateCoercionViaModelValidate:
    """``Filter.model_validate`` (the production path) coerces date strings."""

    @pytest.mark.parametrize("operator", ["eq", "ge", "gt", "le", "lt"])
    def test_iso_date_string_coerced_for_comparison_operators(self, operator: str):
        """Comparison operators parse ``YYYY-MM-DD`` strings into ``date`` objects."""
        f = TransactionFilter.model_validate(
            {"column": "date", "operator": operator, "value": "2025-01-15"},
        )
        assert f.value == date(2025, 1, 15)
        assert isinstance(f.value, date)

    @pytest.mark.parametrize("operator", ["like", "ilike"])
    def test_iso_date_string_preserved_for_pattern_operators(self, operator: str):
        """``like``/``ilike`` keep the original string so wildcards stay intact."""
        f = CategoryFilter.model_validate(
            {"column": "name", "operator": operator, "value": "2025-01-15"},
        )
        assert f.value == "2025-01-15"
        assert isinstance(f.value, str)

    @pytest.mark.parametrize("operator", ["isnull", "notnull"])
    def test_null_operators_do_not_coerce_value(self, operator: str):
        """Null-check operators ignore the value and leave it unchanged."""
        f = CategoryFilter.model_validate(
            {"column": "parent_id", "operator": operator, "value": "2025-01-15"},
        )
        assert f.value == "2025-01-15"

    def test_invalid_date_string_remains_string(self):
        """A malformed date string falls through unchanged."""
        f = CategoryFilter.model_validate(
            {"column": "name", "operator": "eq", "value": "not-a-date"},
        )
        assert f.value == "not-a-date"
        assert isinstance(f.value, str)

    def test_partial_iso_date_remains_string(self):
        """``YYYY-MM`` does not match the full ``%Y-%m-%d`` pattern."""
        f = CategoryFilter.model_validate(
            {"column": "name", "operator": "eq", "value": "2025-01"},
        )
        assert f.value == "2025-01"

    def test_iso_datetime_string_remains_string(self):
        """A full ISO datetime is not the expected ``YYYY-MM-DD`` shape."""
        f = CategoryFilter.model_validate(
            {"column": "name", "operator": "eq", "value": "2025-01-15T10:00:00"},
        )
        assert f.value == "2025-01-15T10:00:00"

    def test_int_value_is_not_coerced(self):
        """Non-string values short-circuit the validator."""
        f = TransactionFilter.model_validate(
            {"column": "product_id", "operator": "eq", "value": 42},
        )
        assert f.value == 42

    def test_float_value_is_not_coerced(self):
        """Float values pass through the validator unchanged."""
        f = TransactionFilter.model_validate(
            {"column": "price", "operator": "gt", "value": 9.99},
        )
        assert f.value == 9.99

    def test_date_value_is_not_recoerced(self):
        """A ``date`` value is already in the desired type and is preserved."""
        target = date(2025, 1, 15)
        f = TransactionFilter.model_validate(
            {"column": "date", "operator": "eq", "value": target},
        )
        assert f.value == target

    def test_none_value_passes_through_for_null_operator(self):
        """``None`` is acceptable for null-check operators."""
        f = CategoryFilter.model_validate(
            {"column": "parent_id", "operator": "isnull", "value": None},
        )
        assert f.value is None


class TestToSqlalchemyFilter:
    """Tests for ``Filter.to_sqlalchemy_filter`` SQL expression rendering."""

    def test_isnull_renders_is_null(self):
        """``isnull`` builds an ``IS NULL`` expression and ignores ``value``."""
        expr = CategoryFilter(
            column="parent_id",
            operator="isnull",
            value=None,
        ).to_sqlalchemy_filter(Category)
        assert isinstance(expr, ColumnElement)
        assert "IS NULL" in _compile(expr).upper()

    def test_notnull_renders_is_not_null(self):
        """``notnull`` builds an ``IS NOT NULL`` expression."""
        expr = CategoryFilter(
            column="parent_id",
            operator="notnull",
            value=None,
        ).to_sqlalchemy_filter(Category)
        assert "IS NOT NULL" in _compile(expr).upper()

    def test_eq_renders_equals(self):
        """``eq`` builds an equality expression with the literal value."""
        expr = CategoryFilter(column="name", operator="eq", value="Food").to_sqlalchemy_filter(Category)
        sql = _compile(expr)
        assert "=" in sql
        assert "Food" in sql

    @pytest.mark.parametrize(
        ("operator", "sql_symbol"),
        [("ge", ">="), ("gt", ">"), ("le", "<="), ("lt", "<")],
    )
    def test_comparison_operators_render_expected_symbol(self, operator: str, sql_symbol: str):
        """Each comparison operator renders its matching SQL symbol."""
        expr = TransactionFilter(
            column="price",
            operator=operator,
            value=10,
        ).to_sqlalchemy_filter(Transaction)
        assert sql_symbol in _compile(expr)

    def test_like_wraps_value_with_percent_wildcards(self):
        """``like`` substring-matches by wrapping the value with ``%`` on both sides."""
        expr = CategoryFilter(column="name", operator="like", value="oo").to_sqlalchemy_filter(Category)
        sql = _compile(expr)
        assert "LIKE" in sql.upper()
        assert "%oo%" in sql

    def test_ilike_wraps_value_with_percent_wildcards(self):
        """``ilike`` mirrors ``like`` but renders the case-insensitive variant."""
        expr = CategoryFilter(column="name", operator="ilike", value="OO").to_sqlalchemy_filter(Category)
        sql = _compile(expr)
        # SQLite renders ilike as ``lower(col) LIKE lower(?)``; other dialects use ILIKE.
        assert "ILIKE" in sql.upper() or "LOWER" in sql.upper()
        assert "%OO%" in sql

    def test_date_comparison_uses_coerced_date_value_via_model_validate(self):
        """A date filter built via ``model_validate`` compares against the coerced ``date``."""
        f = TransactionFilter.model_validate(
            {"column": "date", "operator": "ge", "value": "2025-01-15"},
        )
        assert isinstance(f.value, date)
        expr = f.to_sqlalchemy_filter(Transaction)
        assert isinstance(expr, BinaryExpression)
        assert "2025-01-15" in _compile(expr)

    def test_like_pattern_with_date_like_value_keeps_string(self):
        """``like`` keeps date-shaped strings raw so wildcards in the pattern still work."""
        expr = CategoryFilter(
            column="name",
            operator="like",
            value="2025-01-15",
        ).to_sqlalchemy_filter(Category)
        assert "%2025-01-15%" in _compile(expr)

    def test_uses_column_from_target_model(self):
        """The expression binds to the column on the supplied declarative class."""
        expr = CategoryFilter(column="name", operator="eq", value="Food").to_sqlalchemy_filter(Category)
        assert isinstance(expr, BinaryExpression)
        assert getattr(expr.left, "key", None) == "name"


class TestFilterValidation:
    """Tests for Pydantic-level validation of Filter inputs."""

    def test_invalid_operator_rejected(self):
        """An unsupported operator fails Pydantic validation."""
        with pytest.raises(ValueError):
            CategoryFilter(column="name", operator="invalid_op", value="x")

    def test_dict_construction_via_model_validate(self):
        """A dict input is validated and produces a Filter instance."""
        f = CategoryFilter.model_validate(
            {"column": "name", "operator": "eq", "value": "Food"},
        )
        assert f.column == "name"
        assert f.operator == "eq"
        assert f.value == "Food"
