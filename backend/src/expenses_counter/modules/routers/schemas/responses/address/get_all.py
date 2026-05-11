"""Get all addresses response schema module."""

__all__ = ("GetAllAddressesResponse", "SimpleAddressGet")

from pydantic import Field

from expenses_counter.modules.routers.schemas.base.metadata import PaginationMetadata
from expenses_counter.modules.routers.schemas.base.response import BaseResponseFromModelSchema


class SimpleAddressGet(BaseResponseFromModelSchema):
    """Response model for getting a simple address in list view."""

    id: int = Field(..., description="The unique identifier for the address")
    local_name: str = Field(..., description="The local name or identifier for this address location")
    address: str = Field(..., description="The physical address string")


class GetAllAddressesResponse(BaseResponseFromModelSchema):
    """Response model for getting all addresses."""

    data: list[SimpleAddressGet] = Field(..., description="The list of addresses")
    metadata: PaginationMetadata = Field(..., description="The pagination metadata")
