"""Category GET schema module."""

__all__ = ("CategoryGet",)

from typing import Optional

from pydantic import ConfigDict, Field

from expenses_counter.services.daos.base import BaseSchema


class SimpleCategoryGet(BaseSchema):
    """Pydantic schema for Simple Category GET responses.

    This schema represents a category entity as returned from the API.
    It includes the category's ID and name.
    """

    model_config = ConfigDict(extra="ignore")

    id: int = Field(..., description="The unique identifier for the category")
    name: str = Field(..., description="The name of the category")


class CategoryGet(BaseSchema):
    """Pydantic schema for Category GET responses.

    This schema represents a category entity as returned from the API.
    It includes the category's ID, name, description, and optional parent
    category reference, enabling hierarchical category structures.

    Attributes:
        id: The unique identifier for the category.
        name: The name of the category.
        description: Optional description providing additional details about the category.
        parent: Optional reference to the parent CategoryGet instance. None for top-level categories.
            Uses recursive self-reference to represent hierarchical structures.

    """

    id: int = Field(..., description="The unique identifier for the category")
    name: str = Field(..., description="The name of the category")
    description: str | None = Field(
        None,
        description="Optional description providing additional details about the category",
    )
    parent: Optional["SimpleCategoryGet"] = Field(
        None,
        description="Optional reference to the parent CategoryGet instance. None indicates a top-level category",
    )
