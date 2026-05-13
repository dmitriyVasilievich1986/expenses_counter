"""Unit tests for ``BaseDAO.concat_filters``."""

__all__ = ()

from typing import ClassVar
from unittest.mock import MagicMock

import pytest
from sqlalchemy.sql import ColumnElement

from expenses_counter.services.daos.base import BaseDAO
from expenses_counter.services.database.models.category import Category


class _CategoryDAO(BaseDAO[Category]):
    """Minimal DAO for testing ``concat_filters`` without ``base_filters``."""

    database_model = Category


class _CategoryDAOWithBaseFilters(BaseDAO[Category]):
    """DAO with ``base_filters`` for testing ``concat_filters`` merging."""

    database_model = Category
    base_filters: ClassVar[list[ColumnElement[bool]]] = [Category.name.isnot(None)]


@pytest.fixture
def dao() -> _CategoryDAO:
    """Return a DAO instance with a stub database client.

    ``BaseDAO.__init__`` requires a client or session; ``concat_filters`` does
    not touch either, so a ``MagicMock`` is sufficient.

    Returns:
        _CategoryDAO: DAO instance without base filters.

    """
    return _CategoryDAO(database_client=MagicMock())


@pytest.fixture
def dao_with_base_filters() -> _CategoryDAOWithBaseFilters:
    """Return a DAO instance whose class declares ``base_filters``.

    Returns:
        _CategoryDAOWithBaseFilters: DAO instance with one base filter.

    """
    return _CategoryDAOWithBaseFilters(database_client=MagicMock())


class TestConcatFilters:
    """Tests for ``BaseDAO.concat_filters`` as an instance method."""

    def test_none_filters_no_base_filters_returns_empty(self, dao: _CategoryDAO) -> None:
        """``concat_filters(None)`` with no base filters yields an empty list."""
        assert dao.concat_filters(None) == []

    def test_none_filters_with_base_filters_returns_base(
        self, dao_with_base_filters: _CategoryDAOWithBaseFilters
    ) -> None:
        """``concat_filters(None)`` returns only base filters when no caller filters given."""
        result = dao_with_base_filters.concat_filters(None)
        assert len(result) == 1
        assert isinstance(result[0], ColumnElement)

    def test_empty_list_no_base_filters_returns_empty(self, dao: _CategoryDAO) -> None:
        """``concat_filters([])`` with no base filters yields an empty list."""
        assert dao.concat_filters([]) == []

    def test_dict_filter_is_converted_to_column_element(self, dao: _CategoryDAO) -> None:
        """A dict filter is validated through ``Filter`` and converted to a ``ColumnElement``."""
        filters = [{"column": "name", "operator": "eq", "value": "Food"}]
        result = dao.concat_filters(filters)
        assert len(result) == 1
        assert isinstance(result[0], ColumnElement)

    def test_column_element_passes_through_unchanged(self, dao: _CategoryDAO) -> None:
        """A raw ``ColumnElement`` filter is returned as-is."""
        expr = Category.name == "Food"
        result = dao.concat_filters([expr])
        assert len(result) == 1
        assert result[0] is expr

    def test_base_filters_prepended_before_caller_filters(
        self, dao_with_base_filters: _CategoryDAOWithBaseFilters
    ) -> None:
        """``base_filters`` come first in the merged list."""
        base = _CategoryDAOWithBaseFilters.base_filters[0]
        caller_expr = Category.id > 0

        result = dao_with_base_filters.concat_filters([caller_expr])

        assert len(result) == 2
        assert result[0] is base
        assert result[1] is caller_expr

    def test_dict_filter_with_base_filters_gives_two_elements(
        self, dao_with_base_filters: _CategoryDAOWithBaseFilters
    ) -> None:
        """A dict filter merged with ``base_filters`` produces two ``ColumnElement``s."""
        filters = [{"column": "name", "operator": "like", "value": "Food"}]
        result = dao_with_base_filters.concat_filters(filters)
        assert len(result) == 2
        assert all(isinstance(f, ColumnElement) for f in result)

    def test_isnull_operator(self, dao: _CategoryDAO) -> None:
        """``isnull`` operator produces a valid ``IS NULL`` expression."""
        filters = [{"column": "parent_id", "operator": "isnull", "value": None}]
        result = dao.concat_filters(filters)
        assert len(result) == 1
        assert isinstance(result[0], ColumnElement)

    def test_notnull_operator(self, dao: _CategoryDAO) -> None:
        """``notnull`` operator produces a valid ``IS NOT NULL`` expression."""
        filters = [{"column": "parent_id", "operator": "notnull", "value": None}]
        result = dao.concat_filters(filters)
        assert len(result) == 1
        assert isinstance(result[0], ColumnElement)

    def test_multiple_dict_filters(self, dao: _CategoryDAO) -> None:
        """Multiple dict filters are all converted and returned."""
        filters = [
            {"column": "name", "operator": "eq", "value": "Food"},
            {"column": "parent_id", "operator": "isnull", "value": None},
        ]
        result = dao.concat_filters(filters)
        assert len(result) == 2
        assert all(isinstance(f, ColumnElement) for f in result)

    def test_mixed_dict_and_column_element(self, dao: _CategoryDAO) -> None:
        """Mixed list of dict and ``ColumnElement`` filters is handled correctly."""
        expr = Category.id > 0
        filters = [
            {"column": "name", "operator": "eq", "value": "Food"},
            expr,
        ]
        result = dao.concat_filters(filters)
        assert len(result) == 2
        assert isinstance(result[0], ColumnElement)
        assert result[1] is expr
