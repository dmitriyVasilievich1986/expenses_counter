"""Shop POST schema module."""

__all__ = ("ShopPost",)

from pydantic import Field

from expenses_counter.services.daos.base import BaseSchema


class ShopPost(BaseSchema):
    """Pydantic schema for Shop POST (create) requests.

    This schema is used for creating new shop entities. The name field is
    required, while icon, description, and category_id are optional. This
    allows for flexible shop creation with varying levels of detail.

    Attributes:
        name: Required name of the shop (max 150 characters). Must be unique.
        icon: Optional icon identifier or path representing the shop visually
            (max 150 characters). Used for UI display purposes.
        description: Optional description of the shop. Provides additional
            context or details about the shop, such as location or specialty.
        category_id: Optional category ID to associate this shop with a
            specific category. If None, the shop is not categorized.

    """

    name: str = Field(..., description="The name of the shop")
    icon: str | None = Field(None, description="The icon of the shop")
    description: str | None = Field(None, description="The description of the shop")
    category_id: int | None = Field(None, description="The category id of the shop")
