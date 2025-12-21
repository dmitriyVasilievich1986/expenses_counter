"""Transaction PATCH schema module."""

__all__ = ("TransactionPatch",)

import datetime

from pydantic import Field

from expenses_counter.services.daos.base import BaseSchema


class TransactionPatch(BaseSchema):
    """Pydantic schema for Transaction PATCH (partial update) requests.

    This schema is used for partial updates to transaction entities. All fields
    are optional, allowing clients to update only the fields they wish to modify.
    Fields that are not provided (None) will remain unchanged in the database.

    Attributes:
        date: Optional date of the transaction. If None, the date will not be updated.
        count: Optional count/quantity of the transaction. If None, the count will not be updated.
        price: Optional price of the transaction. If None, the price will not be updated.
        product_id: Optional product ID. If None, the product relationship will not be updated.
        address_id: Optional address ID. If None, the address relationship will not be updated.

    """

    date: datetime.date | None = Field(None, description="The date of the transaction")
    count: float | None = Field(None, description="The count/quantity of the transaction")
    price: float | None = Field(None, description="The price of the transaction")
    product_id: int | None = Field(None, description="The product id of the transaction")
    address_id: int | None = Field(None, description="The address id of the transaction")

