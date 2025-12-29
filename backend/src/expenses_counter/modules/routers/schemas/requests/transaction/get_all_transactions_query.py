"""Get all transactions query schema module."""

__all__ = ("GetAllTransactionsQuery",)

from typing import Literal

from pydantic import Field

from expenses_counter.modules.routers.schemas.base.query import BaseQueryModel


class GetAllTransactionsQuery(BaseQueryModel):
    """Query parameters for getting all transactions."""

    limit: int = Field(default=100, ge=1, le=100, description="The number of transactions to return")
    offset: int = Field(default=0, ge=0, description="The number of transactions to skip")
    sort_by: Literal["id", "date", "count", "price"] = Field(
        default="id", description="The field to sort the transactions by"
    )
    sort_order: Literal["asc", "desc"] = Field(default="asc", description="The order to sort the transactions by")
