"""Category PATCH schema module."""

__all__ = ("CategoryPatch",)

from pydantic import BaseModel, ConfigDict, Field


class CategoryPatch(BaseModel):
    """Pydantic schema for Category PATCH (partial update) requests.

    This schema is used for partial updates to category entities. All fields
    are optional, allowing clients to update only the fields they wish to modify.
    Fields that are not provided (None) will remain unchanged in the database.

    Attributes:
        name: Optional name of the category (1-150 characters). If None, the name
            will not be updated.
        description: Optional description of the category (0-1000 characters).
            If None, the description will not be updated.
        parent_id: Optional parent category ID. If None, the parent relationship
            will not be updated. Set to None explicitly to remove the parent relationship.

    """

    model_config = ConfigDict(from_attributes=True)

    name: str | None = Field(
        None, min_length=1, max_length=150, description="The name of the category"
    )
    description: str | None = Field(
        None,
        min_length=0,
        max_length=1000,
        description="The description of the category",
    )
    parent_id: int | None = Field(None, description="The parent category id")
