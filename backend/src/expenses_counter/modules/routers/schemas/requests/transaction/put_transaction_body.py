"""Put transaction body schema module."""

__all__ = ("PutTransactionBody",)

import datetime

from pydantic import Field

from expenses_counter.modules.routers.schemas.base.request import BaseRequestModel


class PutTransactionBody(BaseRequestModel):
    """Request body for updating a transaction."""

    date: datetime.date = Field(..., description="The date of the transaction")
    count: float = Field(..., ge=0, description="The quantity/count of items in the transaction")
    price: float = Field(..., ge=0, description="The price of the transaction")
    product_id: int = Field(..., description="The product id associated with this transaction")
    address_id: int = Field(..., description="The address id where this transaction occurred")
