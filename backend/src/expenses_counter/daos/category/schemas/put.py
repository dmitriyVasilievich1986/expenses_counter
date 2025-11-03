"""Category PUT schema module."""

__all__ = ("CategoryPut",)


from pydantic import Field

from expenses_counter.daos.base import BaseSchema


class CategoryPut(BaseSchema):
    """Pydantic schema for Category PUT (full update) requests.

    This schema is used for full updates to category entities. All fields should
    be provided, though description and parent_id are optional. This is distinct
    from PATCH operations which allow partial updates. When using PUT, all
    fields are expected to be included in the request body.

    Attributes:
        name: Required name of the category (1-150 characters). Must be unique
            within the context of its parent category.
        description: Optional description of the category (0-1000 characters).
            If not provided, will be set to None.
        parent_id: Optional parent category ID. If None, the category becomes
            a top-level category. If provided, the category becomes a subcategory
            under the specified parent.

    """

    name: str = Field(..., min_length=1, max_length=150, description="The name of the category")
    description: str | None = Field(
        None,
        min_length=0,
        max_length=1000,
        description="The description of the category",
    )
    parent_id: int | None = Field(None, description="The parent category id")
