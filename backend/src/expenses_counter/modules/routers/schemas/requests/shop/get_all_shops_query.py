"""Get all shops query schema module."""

__all__ = ("GetAllShopsQuery",)

from typing import Literal

from pydantic import Field

from expenses_counter.modules.routers.schemas.base.query import BaseQueryModel


class GetAllShopsQuery(BaseQueryModel):
    """Query parameters for getting all shops."""

    limit: int = Field(default=100, ge=1, le=100, description="The number of shops to return")
    offset: int = Field(default=0, ge=0, description="The number of shops to skip")
    sort_by: Literal["id", "name"] = Field(default="id", description="The field to sort the shops by")
    sort_order: Literal["asc", "desc"] = Field(default="asc", description="The order to sort the shops by")
