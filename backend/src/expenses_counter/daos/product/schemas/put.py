"""Product PUT schema module."""

__all__ = ("ProductPut",)

from pydantic import Field

from expenses_counter.daos.base import BaseSchema


class ProductPut(BaseSchema):
    """Pydantic schema for Product PUT (full update) requests.

    This schema is used for full updates to product entities. All fields should
    be provided, though description and sub_category_id are optional. This is distinct
    from PATCH operations which allow partial updates. When using PUT, all
    fields are expected to be included in the request body.

    Attributes:
        name: Required name of the product (1-150 characters).
        description: Optional description of the product (0-1000 characters).
            If not provided, will be set to None.
        sub_category_id: Optional sub category ID. If None, the product becomes
            uncategorized. If provided, the product is associated with the specified category.

    """

    name: str = Field(..., min_length=1, max_length=150, description="The name of the product")
    description: str | None = Field(
        None,
        min_length=0,
        max_length=1000,
        description="The description of the product",
    )
    sub_category_id: int | None = Field(None, description="The sub category id of the product")
