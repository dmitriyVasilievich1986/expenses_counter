"""Get all transactions query schema module."""

__all__ = ("GetAllTransactionsQuery",)

from typing import Literal

from expenses_counter.modules.routers.schemas.base.metadata import PaginationQuery


class GetAllTransactionsQuery(
    PaginationQuery[Literal["id", "date", "count", "price"], Literal["id", "date", "count", "price"]]
):
    """Query parameters for getting all transactions."""

    pass
