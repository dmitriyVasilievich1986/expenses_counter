"""Get all categories query schema module."""

__all__ = ("GetAllProductsQuery",)

from typing import Literal

from expenses_counter.modules.routers.schemas.base.metadata import PaginationWithFiltersQuery


class GetAllProductsQuery(PaginationWithFiltersQuery[Literal["id", "name"], Literal["id", "name", "category_id"]]):
    """Query parameters for getting all products."""

    pass
