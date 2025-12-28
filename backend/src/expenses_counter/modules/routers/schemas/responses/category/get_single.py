"""Get single category response schema module."""

__all__ = ("GetSingleCategoryResponse",)

from typing import Optional

from pydantic import Field

from expenses_counter.modules.routers.schemas.base.response import BaseResponseFromModelSchema


class GetSingleCategoryResponse(BaseResponseFromModelSchema):
    """Response model for getting a single category."""

    id: int = Field(..., description="The unique identifier for the category")
    name: str = Field(..., description="The name of the category")
    description: str | None = Field(None, description="The description of the category")
    parent: Optional["GetSingleCategoryResponse"] = Field(None, description="The parent category")
