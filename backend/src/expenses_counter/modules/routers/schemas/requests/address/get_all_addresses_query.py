"""Get all addresses query schema module."""

__all__ = ("GetAllAddressesQuery",)

from typing import Literal

from pydantic import Field

from expenses_counter.modules.routers.schemas.base.query import BaseQueryModel


class GetAllAddressesQuery(BaseQueryModel):
    """Query parameters for getting all addresses."""

    limit: int = Field(default=100, ge=1, le=100, description="The number of addresses to return")
    offset: int = Field(default=0, ge=0, description="The number of addresses to skip")
    sort_by: Literal["id", "local_name", "address"] = Field(
        default="id", description="The field to sort the addresses by"
    )
    sort_order: Literal["asc", "desc"] = Field(default="asc", description="The order to sort the addresses by")
