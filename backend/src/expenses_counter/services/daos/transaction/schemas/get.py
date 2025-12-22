"""Transaction GET schema module."""

__all__ = ("TransactionGet",)

import datetime

from pydantic import Field

from expenses_counter.services.daos.address.schemas.get import SimpleAddressGet
from expenses_counter.services.daos.base import BaseSchema
from expenses_counter.services.daos.product.schemas.get import SimpleProductGet


class TransactionGet(BaseSchema):
    """Pydantic schema for Transaction GET responses.

    This schema represents a transaction entity as returned from the API.
    It includes the transaction's ID, date, count, price, and references to
    product and address.

    Attributes:
        id: The unique identifier for the transaction.
        date: The date of the transaction.
        count: The count/quantity of the transaction.
        price: The price of the transaction.
        product: Reference to the SimpleProductGet instance associated with this transaction.
        address: Reference to the SimpleAddressGet instance associated with this transaction.

    """

    id: int = Field(..., description="The unique identifier for the transaction")
    date: datetime.date = Field(..., description="The date of the transaction")
    count: float = Field(..., description="The count/quantity of the transaction")
    price: float = Field(..., description="The price of the transaction")
    product: "SimpleProductGet" = Field(
        ...,
        description="Reference to the SimpleProductGet instance associated with this transaction",
    )
    address: "SimpleAddressGet" = Field(
        ...,
        description="Reference to the SimpleAddressGet instance associated with this transaction",
    )
