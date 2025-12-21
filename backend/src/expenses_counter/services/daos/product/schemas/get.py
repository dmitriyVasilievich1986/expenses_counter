"""Product GET schema module."""

__all__ = ("ProductGet", "SimpleProductGet")

from typing import Optional

from pydantic import ConfigDict, Field

from expenses_counter.services.daos.base import BaseSchema
from expenses_counter.services.daos.category.schemas.get import SimpleCategoryGet


class SimpleProductGet(BaseSchema):
    """Pydantic schema for Simple Product GET responses.

    This schema represents a product entity as returned from the API.
    It includes the product's ID and name.
    """

    model_config = ConfigDict(extra="ignore")

    id: int = Field(..., description="The unique identifier for the product")
    name: str = Field(..., description="The name of the product")


class ProductGet(BaseSchema):
    """Pydantic schema for Product GET responses.

    This schema represents a product entity as returned from the API.
    It includes the product's ID, name, description, and optional sub_category
    reference.

    Attributes:
        id: The unique identifier for the product.
        name: The name of the product.
        description: Optional description providing additional details about the product.
        sub_category: Optional reference to the SimpleCategoryGet instance that this
            product belongs to. None if the product is not categorized.

    """

    id: int = Field(..., description="The unique identifier for the product")
    name: str = Field(..., description="The name of the product")
    description: str | None = Field(
        None,
        description="Optional description providing additional details about the product",
    )
    sub_category: Optional["SimpleCategoryGet"] = Field(
        None,
        description="Optional reference to the SimpleCategoryGet instance. None indicates the product is not categorized",  # noqa: E501
    )
