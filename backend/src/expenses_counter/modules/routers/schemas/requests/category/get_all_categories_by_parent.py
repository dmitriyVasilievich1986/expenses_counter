"""Get all categories query schema module."""

__all__ = ("GetAllCategoriesByParentQuery",)

from typing import Literal

from expenses_counter.modules.routers.schemas.base.metadata import PaginationQuery


class GetAllCategoriesByParentQuery(PaginationQuery[Literal["id", "name"]]):
    """Query parameters for getting all categories by parent."""

    pass
