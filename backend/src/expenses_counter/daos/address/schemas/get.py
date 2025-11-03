"""Address GET schema module."""

__all__ = ("AddressGet", "SimpleAddressGet")


from pydantic import ConfigDict, Field

from expenses_counter.daos.base import BaseSchema
from expenses_counter.daos.shop.schemas.get import SimpleShopGet


class SimpleAddressGet(BaseSchema):
    """Pydantic schema for Simple Address GET responses.

    This schema represents an address entity as returned from the API.
    It includes the address's ID and local name.
    """

    model_config = ConfigDict(extra="ignore")

    id: int = Field(..., description="The unique identifier for the address")
    local_name: str = Field(..., description="The local name or identifier for this address location")


class AddressGet(BaseSchema):
    """Pydantic schema for Address GET responses.

    This schema represents an address entity as returned from the API.
    It includes the address's ID, local name, address string, and optional
    shop reference.

    Attributes:
        id: The unique identifier for the address.
        localName: The local name or identifier for this address location.
        address: The physical address string.
        shop: Optional reference to the shop that owns this address.

    """

    id: int = Field(..., description="The unique identifier for the address")
    local_name: str = Field(..., description="The local name or identifier for this address location")
    address: str = Field(..., description="The physical address string")
    shop: "SimpleShopGet" = Field(
        ...,
        description="Optional reference to the shop that owns this address",
    )
