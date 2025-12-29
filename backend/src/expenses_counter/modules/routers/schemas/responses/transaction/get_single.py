"""Get single transaction response schema module."""

__all__ = ("GetSingleTransactionResponse", "SimpleAddressForTransactionGet", "SimpleProductForTransactionGet")

import datetime

from pydantic import Field

from expenses_counter.modules.routers.schemas.base.response import BaseResponseFromModelSchema


class SimpleProductForTransactionGet(BaseResponseFromModelSchema):
    """Response model for getting a simple product reference in transaction."""

    id: int = Field(..., description="The unique identifier for the product")
    name: str = Field(..., description="The name of the product")


class SimpleAddressForTransactionGet(BaseResponseFromModelSchema):
    """Response model for getting a simple address reference in transaction."""

    id: int = Field(..., description="The unique identifier for the address")
    local_name: str = Field(..., description="The local name of the address")
    address: str = Field(..., description="The physical address string")


class GetSingleTransactionResponse(BaseResponseFromModelSchema):
    """Response model for getting a single transaction."""

    id: int = Field(..., description="The unique identifier for the transaction")
    date: datetime.date = Field(..., description="The date of the transaction")
    count: float = Field(..., description="The quantity/count of items in the transaction")
    price: float = Field(..., description="The price of the transaction")
    product: SimpleProductForTransactionGet = Field(..., description="The product associated with this transaction")
    address: SimpleAddressForTransactionGet = Field(..., description="The address where this transaction occurred")
