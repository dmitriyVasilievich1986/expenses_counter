"""Get all transactions query schema module."""

__all__ = ("GetAllTransactionsQuery",)

from typing import Literal

from expenses_counter.modules.routers.schemas.base.metadata import PaginationWithFiltersQuery


class GetAllTransactionsQuery(
    PaginationWithFiltersQuery[Literal["id", "date", "count", "price"], Literal["id", "date", "count", "price"]]
):
    """Query parameters for getting all transactions."""

    pass
