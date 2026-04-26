"""Get all addresses query schema module."""

__all__ = ("GetAllAddressesQuery",)

from typing import Literal

from pydantic import Field

from expenses_counter.modules.routers.schemas.base.metadata import PaginationQuery


class GetAllAddressesQuery(PaginationQuery):
    """Query parameters for getting all addresses."""

    sort_by: Literal["id", "local_name", "address"] = Field(
        default="id", description="The field to sort the addresses by"
    )
