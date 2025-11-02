"""Category POST schema module."""

__all__ = ("CategoryPost",)


from pydantic import Field

from expenses_counter.daos.base import BaseSchema


class CategoryPost(BaseSchema):
    """Pydantic schema for Category POST (create) requests.

    This schema is used for creating new category entities. The name field is
    required, while description and parent_id are optional. This allows for
    both top-level categories (when parent_id is None) and nested categories
    within a hierarchical structure.

    Attributes:
        name: Required name of the category (1-150 characters). Must be unique
            within the context of its parent category.
        description: Optional description of the category (0-1000 characters).
            Provides additional context or details about the category.
        parent_id: Optional parent category ID. If None, creates a top-level
            category. If provided, creates a subcategory under the specified parent.

    """

    name: str = Field(
        ..., min_length=1, max_length=150, description="The name of the category"
    )
    description: str | None = Field(
        None,
        min_length=0,
        max_length=1000,
        description="The description of the category",
    )
    parent_id: int | None = Field(None, description="The parent category id")
