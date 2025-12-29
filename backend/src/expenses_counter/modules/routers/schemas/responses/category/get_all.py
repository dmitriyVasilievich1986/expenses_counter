"""Get all categories response schema module."""

__all__ = ("GetAllCategoriesResponse", "SimpleCategoryGet")

from pydantic import Field

from expenses_counter.modules.routers.schemas.base import BaseResponseFromModelSchema, PaginationMetadata


class SimpleCategoryGet(BaseResponseFromModelSchema):
    """Response model for getting a single category."""

    id: int = Field(..., description="The unique identifier for the category")
    name: str = Field(..., description="The name of the category")


class GetAllCategoriesResponse(BaseResponseFromModelSchema):
    """Response model for getting all categories."""

    data: list[SimpleCategoryGet] = Field(..., description="The list of categories")
    metadata: PaginationMetadata = Field(..., description="The pagination metadata")
