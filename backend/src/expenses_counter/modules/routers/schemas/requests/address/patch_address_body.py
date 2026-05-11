"""Patch address body schema module."""

__all__ = ("PatchAddressBody",)

from pydantic import Field

from expenses_counter.modules.routers.schemas.base.request import BaseRequestModel


class PatchAddressBody(BaseRequestModel):
    """Request body for updating an address."""

    local_name: str | None = Field(
        None, min_length=1, max_length=150, description="The local name or identifier for this address location"
    )
    address: str | None = Field(None, min_length=1, max_length=150, description="The physical address string")
    shop_id: int | None = Field(None, description="The shop id that owns this address")
