"""Product PATCH schema module."""

__all__ = ("ProductPatch",)

from pydantic import Field

from expenses_counter.services.daos.base import BaseSchema


class ProductPatch(BaseSchema):
    """Pydantic schema for Product PATCH (partial update) requests.

    This schema is used for partial updates to product entities. All fields
    are optional, allowing clients to update only the fields they wish to modify.
    Fields that are not provided (None) will remain unchanged in the database.

    Attributes:
        name: Optional name of the product (1-150 characters). If None, the name
            will not be updated.
        description: Optional description of the product (0-1000 characters).
            If None, the description will not be updated.
        sub_category_id: Optional sub category ID. If None, the sub_category relationship
            will not be updated. Set to None explicitly to remove the sub_category relationship.

    """

    name: str | None = Field(None, min_length=1, max_length=150, description="The name of the product")
    description: str | None = Field(
        None,
        min_length=0,
        max_length=1000,
        description="The description of the product",
    )
    sub_category_id: int | None = Field(None, description="The sub category id of the product")
