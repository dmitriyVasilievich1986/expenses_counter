"""Shop GET schema module."""

__all__ = ("ShopGet",)


from pydantic import ConfigDict, Field

from expenses_counter.daos.base import BaseSchema
from expenses_counter.daos.category.schemas.get import SimpleCategoryGet


class SimpleShopGet(BaseSchema):
    """Pydantic schema for Simple Shop GET responses.

    This schema represents a shop entity as returned from the API.
    It includes the shop's ID and name.
    """

    model_config = ConfigDict(extra="ignore")

    id: int = Field(..., description="The unique identifier for the shop")
    name: str = Field(..., description="The name of the shop")


class ShopGet(BaseSchema):
    """Pydantic schema for Shop GET responses.

    This schema represents a shop entity as returned from the API.
    It includes the shop's ID, name, optional icon, description, and
    optional category reference.

    Attributes:
        id: The unique identifier for the shop.
        name: The name of the shop.
        icon: Optional icon representing the shop visually.
        description: Optional description providing additional details about the shop.
        category: Optional reference to the SimpleCategoryGet instance associated with this shop.

    """

    id: int = Field(..., description="The unique identifier for the shop")
    name: str = Field(..., description="The name of the shop")
    icon: str | None = Field(None, description="The icon of the shop")
    description: str | None = Field(None, description="The description of the shop")
    category: SimpleCategoryGet | None = Field(None, description="The category of the shop")
