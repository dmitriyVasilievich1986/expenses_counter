"""Post address body schema module."""

__all__ = ("PostAddressBody",)

from pydantic import Field

from expenses_counter.modules.routers.schemas.base.request import BaseRequestModel


class PostAddressBody(BaseRequestModel):
    """Request body for creating an address."""

    local_name: str = Field(
        ..., min_length=1, max_length=150, description="The local name or identifier for this address location"
    )
    address: str = Field(..., min_length=1, max_length=150, description="The physical address string")
    shop_id: int = Field(..., description="The shop id that owns this address")
