from typing import Literal

from pydantic import Field

from expenses_counter.modules.routers.schemas.base.query import BaseQueryModel


class MonthlyQuery(BaseQueryModel):
    """Query parameters for getting monthly transactions."""

    sort_by: Literal["id", "date", "count", "price"] = Field("id", description="The field to sort the parameters by")
    sort_order: Literal["asc", "desc"] = Field("asc", description="The order to sort the parameters by")
