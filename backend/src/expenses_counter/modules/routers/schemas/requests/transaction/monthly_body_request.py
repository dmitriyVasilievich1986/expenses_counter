import datetime

from pydantic import Field

from expenses_counter.modules.routers.schemas.base.request import BaseRequestModel


class MonthlyBodyRequest(BaseRequestModel):
    """Request body for getting monthly transactions."""

    date: datetime.date = Field(..., description="The date from which the monthly transactions are to be retrieved")
