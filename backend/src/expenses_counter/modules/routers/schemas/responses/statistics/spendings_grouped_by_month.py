"""Spendings grouped by month response schema module."""

__all__ = ("SpendingsGroupedByMonthResponse",)

import datetime

from pydantic import Field

from expenses_counter.modules.routers.schemas.base.response import BaseResponseFromModelSchema


class SpendingsGroupedByMonthResponse(BaseResponseFromModelSchema):
    """Response model for getting the spendings grouped by month."""

    month: datetime.date = Field(..., description="The month of the spendings")
    spendings: float = Field(..., description="The spendings for the month")
