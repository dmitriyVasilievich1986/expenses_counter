"""Product price body schema module."""

__all__ = ("ProductPriceBody",)

from pydantic import Field

from expenses_counter.modules.routers.schemas.base.request import BaseRequestModel


class ProductPriceBody(BaseRequestModel):
    """Request body for getting the product price."""

    product_ids: list[int] = Field(..., description="The product ids")
