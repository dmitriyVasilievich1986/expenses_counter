"""Get all shops query schema module."""

__all__ = ("GetAllShopsQuery",)

from typing import Literal

from expenses_counter.modules.routers.schemas.base.metadata import PaginationWithFiltersQuery


class GetAllShopsQuery(PaginationWithFiltersQuery[Literal["id", "name"], Literal["id", "name", "category_id"]]):
    """Query parameters for getting all shops."""

    pass
