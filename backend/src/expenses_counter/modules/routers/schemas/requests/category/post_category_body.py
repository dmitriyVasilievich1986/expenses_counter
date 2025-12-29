"""Post category body schema module."""

__all__ = ("PostCategoryBody",)

from pydantic import Field

from expenses_counter.modules.routers.schemas.base.request import BaseRequestModel


class PostCategoryBody(BaseRequestModel):
    """Request body for creating a category."""

    name: str = Field(..., min_length=1, max_length=150, description="The name of the category")
    description: str | None = Field(None, min_length=0, max_length=1000, description="The description of the category")
    parent_id: int | None = Field(None, description="The parent category id")
