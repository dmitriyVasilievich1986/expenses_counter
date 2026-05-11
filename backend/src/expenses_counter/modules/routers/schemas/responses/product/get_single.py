"""Get single product response schema module."""

from pydantic import Field

from expenses_counter.modules.routers.schemas.base.response import BaseResponseFromModelSchema
from expenses_counter.modules.routers.schemas.responses.category import SimpleCategoryGet

__all__ = ("GetSingleProductResponse",)


class GetSingleProductResponse(BaseResponseFromModelSchema):
    """Response model for getting a single product."""

    id: int = Field(..., description="The unique identifier for the product")
    name: str = Field(..., description="The name of the product")
    description: str | None = Field(None, description="The description of the product")
    category_id: int | None = Field(None, description="The category id of the product")
    category: SimpleCategoryGet | None = Field(None, description="The category of the product")
