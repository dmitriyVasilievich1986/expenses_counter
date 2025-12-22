"""Transaction PUT schema module."""

__all__ = ("TransactionPut",)

import datetime

from pydantic import Field

from expenses_counter.services.daos.base import BaseSchema


class TransactionPut(BaseSchema):
    """Pydantic schema for Transaction PUT (full update) requests.

    This schema is used for full updates to transaction entities. All fields should
    be provided. This is distinct from PATCH operations which allow partial updates.
    When using PUT, all fields are expected to be included in the request body.

    Attributes:
        date: Required date of the transaction.
        count: Required count/quantity of the transaction.
        price: Required price of the transaction.
        product_id: Required product ID that this transaction is associated with.
        address_id: Required address ID that this transaction is associated with.

    """

    date: datetime.date = Field(..., description="The date of the transaction")
    count: float = Field(..., description="The count/quantity of the transaction")
    price: float = Field(..., description="The price of the transaction")
    product_id: int = Field(..., description="The product id of the transaction")
    address_id: int = Field(..., description="The address id of the transaction")
