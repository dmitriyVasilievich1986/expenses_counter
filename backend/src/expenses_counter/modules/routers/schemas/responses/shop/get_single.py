"""Get single shop response schema module."""

__all__ = ("GetSingleShopResponse",)

from pydantic import Field

from expenses_counter.modules.routers.schemas.base.response import BaseResponseFromModelSchema
from expenses_counter.modules.routers.schemas.responses.category import SimpleCategoryGet


class GetSingleShopResponse(BaseResponseFromModelSchema):
    """Response model for getting a single shop."""

    id: int = Field(..., description="The unique identifier for the shop")
    name: str = Field(..., description="The name of the shop")
    icon: str | None = Field(None, description="Optional icon representing the shop visually")
    description: str | None = Field(
        None, description="Optional description providing additional details about the shop"
    )
    category: SimpleCategoryGet | None = Field(None, description="The category that classifies this shop")
