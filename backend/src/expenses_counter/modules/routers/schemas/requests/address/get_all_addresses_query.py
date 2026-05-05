"""Get all addresses query schema module."""

__all__ = ("GetAllAddressesQuery",)

from typing import Literal

from expenses_counter.modules.routers.schemas.base.metadata import PaginationWithFiltersQuery


class GetAllAddressesQuery(
    PaginationWithFiltersQuery[Literal["id", "local_name", "address"], Literal["id", "local_name", "address"]]
):
    """Query parameters for getting all addresses."""

    pass
