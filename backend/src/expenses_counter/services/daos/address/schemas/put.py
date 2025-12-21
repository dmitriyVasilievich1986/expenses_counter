"""Address PUT schema module."""

__all__ = ("AddressPut",)


from pydantic import Field

from expenses_counter.services.daos.base import BaseSchema


class AddressPut(BaseSchema):
    """Pydantic schema for Address PUT (full update) requests.

    This schema is used for full updates to address entities. All fields should
    be provided, including the shop_id. This is distinct from PATCH operations
    which allow partial updates. When using PUT, all fields are expected to be
    included in the request body.

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
