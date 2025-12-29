"""Get all products response schema module."""

__all__ = ("GetAllProductsResponse", "SimpleProductGet")

from pydantic import Field

from expenses_counter.modules.routers.schemas.base.metadata import PaginationMetadata
from expenses_counter.modules.routers.schemas.base.response import BaseResponseFromModelSchema


class SimpleProductGet(BaseResponseFromModelSchema):
    """Response model for getting a single product."""

    id: int = Field(..., description="The unique identifier for the product")
    name: str = Field(..., description="The name of the product")


class GetAllProductsResponse(BaseResponseFromModelSchema):
    """Response model for getting all products."""

    data: list[SimpleProductGet] = Field(..., description="The list of products")
    metadata: PaginationMetadata = Field(..., description="The pagination metadata")
