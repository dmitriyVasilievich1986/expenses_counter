"""Product POST schema module."""

__all__ = ("ProductPost",)

from pydantic import Field

from expenses_counter.daos.base import BaseSchema


class ProductPost(BaseSchema):
    """Pydantic schema for Product POST (create) requests.

    This schema is used for creating new product entities. The name field is
    required, while description and sub_category_id are optional. This allows for
    flexible product creation with varying levels of detail.

    Attributes:
        name: Required name of the product (1-150 characters).
        description: Optional description of the product (0-1000 characters).
            Provides additional context or details about the product.
        sub_category_id: Optional sub category ID. If None, the product is not
            categorized. If provided, associates the product with the specified category.

    """

    name: str = Field(..., min_length=1, max_length=150, description="The name of the product")
    description: str | None = Field(
        None,
        min_length=0,
        max_length=1000,
        description="The description of the product",
    )
    sub_category_id: int | None = Field(None, description="The sub category id of the product")
