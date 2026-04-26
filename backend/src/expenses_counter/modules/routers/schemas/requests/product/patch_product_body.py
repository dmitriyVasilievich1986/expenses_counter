"""Patch product body schema module."""

__all__ = ("PatchProductBody",)

from pydantic import Field

from expenses_counter.modules.routers.schemas.base.request import BaseRequestModel


class PatchProductBody(BaseRequestModel):
    """Request body for patching a product."""

    name: str | None = Field(None, min_length=1, max_length=150, description="The name of the product")
    description: str | None = Field(None, min_length=0, max_length=1000, description="The description of the product")
    category_id: int | None = Field(None, description="The category id of the product")
