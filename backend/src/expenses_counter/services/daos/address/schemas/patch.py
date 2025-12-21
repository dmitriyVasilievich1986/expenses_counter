"""Address PATCH schema module."""

__all__ = ("AddressPatch",)

from pydantic import Field

from expenses_counter.services.daos.base import BaseSchema


class AddressPatch(BaseSchema):
    """Pydantic schema for Address PATCH (partial update) requests.

    This schema is used for partial updates to address entities. All fields
    are optional, allowing clients to update only the fields they wish to modify.
    Fields that are not provided (None) will remain unchanged in the database.

    Attributes:
        localName: Optional local name of the address (1-150 characters).
            If None, the local name will not be updated.
        address: Optional physical address string (1-150 characters).
            If None, the address will not be updated.
        shopId: Optional shop ID that owns this address. If None, the shop
            relationship will not be updated.

    """

    local_name: str | None = Field(
        None,
        min_length=1,
        max_length=150,
        description="The local name or identifier for this address location",
    )
    address: str | None = Field(
        None,
        min_length=1,
        max_length=150,
        description="The physical address string",
    )
    shop_id: int | None = Field(None, description="The shop ID that owns this address")
