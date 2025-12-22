"""Transaction POST schema module."""

__all__ = ("TransactionPost",)

import datetime

from pydantic import Field

from expenses_counter.services.daos.base import BaseSchema


class TransactionPost(BaseSchema):
    """Pydantic schema for Transaction POST (create) requests.

    This schema is used for creating new transaction entities. All fields are
    required to create a transaction.

    Attributes:
        date: Required date of the transaction.
        count: Required count/quantity of the transaction (default: 0).
        price: Required price of the transaction (default: 0).
        product_id: Required product ID that this transaction is associated with.
        address_id: Required address ID that this transaction is associated with.

    """

    date: datetime.date = Field(..., description="The date of the transaction")
    count: float = Field(0, description="The count/quantity of the transaction")
    price: float = Field(0, description="The price of the transaction")
    product_id: int = Field(..., description="The product id of the transaction")
    address_id: int = Field(..., description="The address id of the transaction")
