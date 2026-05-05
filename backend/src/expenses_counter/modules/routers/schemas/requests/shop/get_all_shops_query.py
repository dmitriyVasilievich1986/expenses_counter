"""Get all shops query schema module."""

__all__ = ("GetAllShopsQuery",)

from typing import Literal

from expenses_counter.modules.routers.schemas.base.metadata import PaginationQuery


class GetAllShopsQuery(PaginationQuery[Literal["id", "name"], Literal["id", "name"]]):
    """Query parameters for getting all shops."""

    pass
