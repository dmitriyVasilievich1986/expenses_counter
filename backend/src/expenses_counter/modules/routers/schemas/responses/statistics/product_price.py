"""Product price response schema module."""

__all__ = ("ProductPriceResponse",)

import datetime

from pydantic import Field

from expenses_counter.modules.routers.schemas.base.response import BaseResponseFromModelSchema


class ProductPriceResponse(BaseResponseFromModelSchema):
    """Response model for getting the product price."""

    product_id: int = Field(..., description="The product id")
    price: float = Field(..., description="The price of the product")
    date: datetime.date = Field(..., description="The date of the price")
