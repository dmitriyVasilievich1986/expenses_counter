"""Shop PUT schema module."""

__all__ = ("ShopPut",)

from pydantic import Field

from expenses_counter.daos.base import BaseSchema


class ShopPut(BaseSchema):
    """Pydantic schema for Shop PUT (full update) requests.

    This schema is used for full updates to shop entities. All fields should
    be provided, though icon, description, and category_id are optional. This
    is distinct from PATCH operations which allow partial updates. When using
    PUT, all fields are expected to be included in the request body.

    Attributes:
        name: Required name of the shop (max 150 characters). Must be unique.
        icon: Optional icon identifier or path representing the shop visually
            (max 150 characters). If not provided, will be set to None.
        description: Optional description of the shop. If not provided, will
            be set to None.
        category_id: Optional category ID to associate this shop with a
            specific category. If None, the shop will not be categorized.

    """

    name: str = Field(..., description="The name of the shop")
    icon: str | None = Field(None, description="The icon of the shop")
    description: str | None = Field(None, description="The description of the shop")
    category_id: int | None = Field(None, description="The category id of the shop")
