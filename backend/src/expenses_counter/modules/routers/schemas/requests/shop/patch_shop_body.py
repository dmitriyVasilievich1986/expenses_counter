"""Patch shop body schema module."""

__all__ = ("PatchShopBody",)

from pydantic import Field

from expenses_counter.modules.routers.schemas.base.request import BaseRequestModel


class PatchShopBody(BaseRequestModel):
    """Request body for patching a shop."""

    name: str | None = Field(None, min_length=1, max_length=150, description="The name of the shop")
    icon: str | None = Field(None, max_length=150, description="Optional icon representing the shop visually")
    description: str | None = Field(
        None, max_length=10000, description="Optional description providing additional details about the shop"
    )
    category_id: int | None = Field(None, description="The category id that classifies this shop")
