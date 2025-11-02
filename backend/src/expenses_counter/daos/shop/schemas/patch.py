"""Shop PATCH schema module."""

__all__ = ("ShopPatch",)

from pydantic import Field

from expenses_counter.daos.base import BaseSchema


class ShopPatch(BaseSchema):
    """Pydantic schema for Shop PATCH (partial update) requests.

    This schema is used for partial updates to shop entities. All fields
    are optional, allowing clients to update only the fields they wish to modify.
    Fields that are not provided (None) will remain unchanged in the database.

    Attributes:
        name: Optional name of the shop. If None, the name will not be updated.
        icon: Optional icon representing the shop visually. If None, the icon
            will not be updated.
        description: Optional description of the shop. If None, the description
            will not be updated.
        category_id: Optional category ID. If None, the category relationship
            will not be updated. Set to None explicitly to remove the category relationship.

    """

    name: str | None = Field(None, description="The name of the shop")
    icon: str | None = Field(None, description="The icon of the shop")
    description: str | None = Field(None, description="The description of the shop")
    category_id: int | None = Field(None, description="The category id of the shop")
