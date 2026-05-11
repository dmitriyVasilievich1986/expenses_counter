"""Unit tests for BaseDAO.concat_filters class method."""

__all__ = ()

from typing import ClassVar

from sqlalchemy.sql import ColumnElement

from expenses_counter.services.daos.base import BaseDAO
from expenses_counter.services.database.models.category import Category


class _CategoryDAO(BaseDAO[Category]):
    """Minimal DAO for testing concat_filters without base_filters."""

    database_model = Category


class _CategoryDAOWithBaseFilters(BaseDAO[Category]):
    """DAO with base_filters for testing concat_filters merging."""

    database_model = Category
    base_filters: ClassVar[list[ColumnElement[bool]]] = [Category.name.isnot(None)]


class TestConcatFilters:
    """Tests for BaseDAO.concat_filters."""

    def test_none_filters_no_base_filters_returns_empty(self):
        """concat_filters(None) with no base_filters yields an empty list."""
        result = _CategoryDAO.concat_filters(None)
        assert result == []

    def test_none_filters_with_base_filters_returns_base(self):
        """concat_filters(None) returns only base_filters when no caller filters given."""
        result = _CategoryDAOWithBaseFilters.concat_filters(None)
        assert len(result) == 1
        assert isinstance(result[0], ColumnElement)

    def test_empty_list_no_base_filters_returns_empty(self):
        """concat_filters([]) with no base_filters yields an empty list."""
        result = _CategoryDAO.concat_filters([])
        assert result == []

    def test_dict_filter_is_converted_to_column_element(self):
        """A dict filter is validated through Filter and converted to a ColumnElement."""
        filters = [{"column": "name", "operator": "eq", "value": "Food"}]
        result = _CategoryDAO.concat_filters(filters)
        assert len(result) == 1
        assert isinstance(result[0], ColumnElement)

    def test_column_element_passes_through_unchanged(self):
        """A raw ColumnElement filter is returned as-is."""
        expr = Category.name == "Food"
        result = _CategoryDAO.concat_filters([expr])
        assert len(result) == 1
        assert result[0] is expr

    def test_base_filters_prepended_before_caller_filters(self):
        """base_filters come first in the merged list."""
        base = _CategoryDAOWithBaseFilters.base_filters[0]
        caller_expr = Category.id > 0

        result = _CategoryDAOWithBaseFilters.concat_filters([caller_expr])

        assert len(result) == 2
        assert result[0] is base
        assert result[1] is caller_expr

    def test_dict_filter_with_base_filters_gives_two_elements(self):
        """A dict filter merged with base_filters produces two ColumnElements."""
        filters = [{"column": "name", "operator": "like", "value": "Food"}]
        result = _CategoryDAOWithBaseFilters.concat_filters(filters)
        assert len(result) == 2
        assert all(isinstance(f, ColumnElement) for f in result)

    def test_isnull_operator(self):
        """Isnull operator produces a valid IS NULL expression."""
        filters = [{"column": "parent_id", "operator": "isnull", "value": None}]
        result = _CategoryDAO.concat_filters(filters)
        assert len(result) == 1
        assert isinstance(result[0], ColumnElement)

    def test_notnull_operator(self):
        """Notnull operator produces a valid IS NOT NULL expression."""
        filters = [{"column": "parent_id", "operator": "notnull", "value": None}]
        result = _CategoryDAO.concat_filters(filters)
        assert len(result) == 1
        assert isinstance(result[0], ColumnElement)

    def test_multiple_dict_filters(self):
        """Multiple dict filters are all converted and returned."""
        filters = [
            {"column": "name", "operator": "eq", "value": "Food"},
            {"column": "parent_id", "operator": "isnull", "value": None},
        ]
        result = _CategoryDAO.concat_filters(filters)
        assert len(result) == 2
        assert all(isinstance(f, ColumnElement) for f in result)

    def test_mixed_dict_and_column_element(self):
        """Mixed list of dict and ColumnElement filters is handled correctly."""
        expr = Category.id > 0
        filters = [
            {"column": "name", "operator": "eq", "value": "Food"},
            expr,
        ]
        result = _CategoryDAO.concat_filters(filters)
        assert len(result) == 2
        assert isinstance(result[0], ColumnElement)
        assert result[1] is expr
