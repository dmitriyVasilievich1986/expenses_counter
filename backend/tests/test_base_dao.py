"""Unit tests for ``BaseDAO.parse_filters`` and ``BaseDAO.concat_filters``."""

__all__ = ()

from typing import ClassVar

import pytest
from sqlalchemy.sql import ColumnElement

from expenses_counter.services.daos.base import BaseDAO
from expenses_counter.services.database.models.category import Category
from expenses_counter.utils.filter import Filter


class _CategoryDAO(BaseDAO[Category]):
    """Minimal DAO for testing filter helpers without ``base_filters``."""

    database_model = Category


class _CategoryDAOWithBaseFilters(BaseDAO[Category]):
    """DAO with ``base_filters`` for tests that need to merge them explicitly."""

    database_model = Category
    base_filters: ClassVar[list[ColumnElement[bool]]] = [Category.name.isnot(None)]


class TestParseFilters:
    """Tests for ``BaseDAO.parse_filters`` as a classmethod."""

    def test_none_returns_empty(self) -> None:
        """``parse_filters(None)`` yields an empty list."""
        assert _CategoryDAO.parse_filters(None) == []

    def test_empty_list_returns_empty(self) -> None:
        """``parse_filters([])`` yields an empty list."""
        assert _CategoryDAO.parse_filters([]) == []

    def test_dict_filter_is_converted_to_column_element(self) -> None:
        """A dict filter is validated through ``Filter`` and converted."""
        filters = [{"column": "name", "operator": "eq", "value": "Food"}]
        result = _CategoryDAO.parse_filters(filters)
        assert len(result) == 1
        assert isinstance(result[0], ColumnElement)

    def test_column_element_passes_through_unchanged(self) -> None:
        """A raw ``ColumnElement`` filter is returned as-is."""
        expr = Category.name == "Food"
        result = _CategoryDAO.parse_filters([expr])
        assert len(result) == 1
        assert result[0] is expr

    def test_filter_instance_is_converted_to_column_element(self) -> None:
        """A ``Filter`` model is converted via ``to_sqlalchemy_filter``."""
        filter_: Filter[str] = Filter(column="name", operator="eq", value="Food")
        result = _CategoryDAO.parse_filters([filter_])
        assert len(result) == 1
        assert isinstance(result[0], ColumnElement)

    def test_isnull_operator(self) -> None:
        """``isnull`` operator produces a valid ``IS NULL`` expression."""
        filters = [{"column": "parent_id", "operator": "isnull", "value": None}]
        result = _CategoryDAO.parse_filters(filters)
        assert len(result) == 1
        assert isinstance(result[0], ColumnElement)

    def test_notnull_operator(self) -> None:
        """``notnull`` operator produces a valid ``IS NOT NULL`` expression."""
        filters = [{"column": "parent_id", "operator": "notnull", "value": None}]
        result = _CategoryDAO.parse_filters(filters)
        assert len(result) == 1
        assert isinstance(result[0], ColumnElement)

    def test_unknown_type_raises_value_error(self) -> None:
        """An entry of an unsupported type raises ``ValueError``."""
        with pytest.raises(ValueError, match="Unknown filter type"):
            _CategoryDAO.parse_filters(["not a filter"])  # type: ignore[list-item]


class TestConcatFilters:
    """Tests for ``BaseDAO.concat_filters`` as a variadic classmethod."""

    def test_no_arguments_returns_empty(self) -> None:
        """``concat_filters()`` with no payloads yields an empty list."""
        assert _CategoryDAO.concat_filters() == []

    def test_single_none_returns_empty(self) -> None:
        """``concat_filters(None)`` yields an empty list."""
        assert _CategoryDAO.concat_filters(None) == []

    def test_single_dict_filter(self) -> None:
        """A single dict filter is parsed into one ``ColumnElement``."""
        filters = [{"column": "name", "operator": "eq", "value": "Food"}]
        result = _CategoryDAO.concat_filters(filters)
        assert len(result) == 1
        assert isinstance(result[0], ColumnElement)

    def test_base_filters_merged_when_passed_explicitly(self) -> None:
        """Two payloads are concatenated in the order they were passed."""
        base = _CategoryDAOWithBaseFilters.base_filters[0]
        caller_expr = Category.id > 0

        result = _CategoryDAOWithBaseFilters.concat_filters(
            _CategoryDAOWithBaseFilters.base_filters,
            [caller_expr],
        )

        assert len(result) == 2
        assert result[0] is base
        assert result[1] is caller_expr

    def test_multiple_payloads_concatenate_in_order(self) -> None:
        """All filter payloads are concatenated in argument order."""
        expr_a = Category.id > 0
        expr_b = Category.name == "Food"

        result = _CategoryDAO.concat_filters([expr_a], [expr_b])

        assert result == [expr_a, expr_b]

    def test_none_payloads_are_skipped(self) -> None:
        """``None`` payloads contribute no clauses."""
        expr = Category.id > 0
        result = _CategoryDAO.concat_filters(None, [expr], None)
        assert result == [expr]

    def test_mixed_dict_and_column_element(self) -> None:
        """Mixed list of dict and ``ColumnElement`` filters is handled correctly."""
        expr = Category.id > 0
        filters = [
            {"column": "name", "operator": "eq", "value": "Food"},
            expr,
        ]
        result = _CategoryDAO.concat_filters(filters)
        assert len(result) == 2
        assert isinstance(result[0], ColumnElement)
        assert result[1] is expr
