"""Get all categories query schema module."""

__all__ = ("GetAllCategoriesQuery",)

from typing import Literal

from pydantic import Field

from expenses_counter.modules.routers.schemas.base.query import BaseQueryModel


class GetAllCategoriesQuery(BaseQueryModel):
    """Query parameters for getting all categories."""

    limit: int = Field(default=100, ge=1, le=100, description="The number of categories to return")
    offset: int = Field(default=0, ge=0, description="The number of categories to skip")
    sort_by: Literal["id", "name"] = Field(default="id", description="The field to sort the categories by")
    sort_order: Literal["asc", "desc"] = Field(default="asc", description="The order to sort the categories by")
