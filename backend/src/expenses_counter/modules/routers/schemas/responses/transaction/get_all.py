"""Get all transactions response schema module."""

__all__ = ("GetAllTransactionsResponse", "SimpleTransactionGet")

import datetime

from pydantic import Field

from expenses_counter.modules.routers.schemas.base.metadata import PaginationMetadata
from expenses_counter.modules.routers.schemas.base.response import BaseResponseFromModelSchema
from expenses_counter.modules.routers.schemas.responses.address import SimpleAddressGet
from expenses_counter.modules.routers.schemas.responses.product import SimpleProductGet


class SimpleTransactionGet(BaseResponseFromModelSchema):
    """Response model for getting a simple transaction in list view."""

    id: int = Field(..., description="The unique identifier for the transaction")
    date: datetime.date = Field(..., description="The date of the transaction")
    count: float = Field(..., description="The quantity/count of items in the transaction")
    price: float = Field(..., description="The price of the transaction")
    product_id: int = Field(..., description="The product id associated with this transaction")
    address_id: int = Field(..., description="The address id where this transaction occurred")
    product: SimpleProductGet = Field(..., description="The product associated with this transaction")
    address: SimpleAddressGet = Field(..., description="The address associated with this transaction")


class GetAllTransactionsResponse(BaseResponseFromModelSchema):
    """Response model for getting all transactions."""

    data: list[SimpleTransactionGet] = Field(..., description="The list of transactions")
    metadata: PaginationMetadata = Field(..., description="The pagination metadata")
