"""Get all categories query schema module."""

__all__ = ("GetAllCategoriesQuery",)

from typing import Literal

from expenses_counter.modules.routers.schemas.base.metadata import PaginationQuery


class GetAllCategoriesQuery(PaginationQuery[Literal["id", "name"], Literal["id", "name"]]):
    """Query parameters for getting all categories."""

    pass
