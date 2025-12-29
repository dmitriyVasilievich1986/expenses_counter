"""Get single address response schema module."""

__all__ = ("GetSingleAddressResponse", "SimpleShopGet")

from pydantic import Field

from expenses_counter.modules.routers.schemas.base.response import BaseResponseFromModelSchema


class SimpleShopGet(BaseResponseFromModelSchema):
    """Response model for getting a simple shop reference."""

    id: int = Field(..., description="The unique identifier for the shop")
    name: str = Field(..., description="The name of the shop")


class GetSingleAddressResponse(BaseResponseFromModelSchema):
    """Response model for getting a single address."""

    id: int = Field(..., description="The unique identifier for the address")
    local_name: str = Field(..., description="The local name or identifier for this address location")
    address: str = Field(..., description="The physical address string")
    shop: SimpleShopGet = Field(..., description="The shop that owns this address")
