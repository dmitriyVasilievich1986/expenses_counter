"""Address POST schema module."""

__all__ = ("AddressPost",)


from pydantic import Field

from expenses_counter.daos.base import BaseSchema


class AddressPost(BaseSchema):
    """Pydantic schema for Address POST (create) requests.

    This schema is used for creating new address entities. All fields are
    required, including the shop_id which links the address to a specific shop.

    Attributes:
        localName: Required local name of the address (1-150 characters).
            Examples: "Headquarters", "Branch 1".
        address: Required physical address string (1-150 characters).
            Contains the street address, city, or other location details.
        shopId: Required shop ID that owns this address. The shop must exist
            in the database.

    """

    local_name: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="The local name or identifier for this address location",
    )
    address: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="The physical address string",
    )
    shop_id: int = Field(..., description="The shop ID that owns this address")
