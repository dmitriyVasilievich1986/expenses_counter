"""Get all shops response schema module."""

__all__ = ("GetAllShopsResponse", "SimpleShopGet")

from pydantic import Field

from expenses_counter.modules.routers.schemas.base.metadata import PaginationMetadata
from expenses_counter.modules.routers.schemas.base.response import BaseResponseFromModelSchema


class SimpleShopGet(BaseResponseFromModelSchema):
    """Response model for getting a simple shop in list view."""

    id: int = Field(..., description="The unique identifier for the shop")
    name: str = Field(..., description="The name of the shop")
    description: str | None = Field(None, description="The description of the shop")
    icon: str | None = Field(None, description="The icon of the shop")
    category_id: int | None = Field(None, description="The category id of the shop")


class GetAllShopsResponse(BaseResponseFromModelSchema):
    """Response model for getting all shops."""

    data: list[SimpleShopGet] = Field(..., description="The list of shops")
    metadata: PaginationMetadata = Field(..., description="The pagination metadata")
