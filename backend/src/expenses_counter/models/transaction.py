"""Transaction model module."""

__all__ = ("Transaction",)

import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, relationship

from .base import Base

if TYPE_CHECKING:
    from expenses_counter.models.address import Address
    from expenses_counter.models.product import Product

class Transaction(Base):
    """SQLAlchemy model representing a Transaction entity.

    Transactions represent financial transactions associated with products and addresses.
    Each transaction belongs to a specific product and address and contains information
    about the date, count, and price of the transaction.
    """

    __tablename__ = "main_transaction"

    id: int = Column[int](Integer, primary_key=True, autoincrement=True)
    date: datetime.date = Column[datetime.date](Date, nullable=False)
    count: float = Column[float](Numeric[float](precision=10, scale=3, asdecimal=True), nullable=False, default=0)
    price: float = Column[float](Numeric[float](precision=10, scale=2, asdecimal=True), nullable=False, default=0)

    product_id: int = Column[int](ForeignKey("main_product.id"), nullable=False)
    product: Mapped["Product"] = relationship("Product", back_populates="transactions")

    address_id: int = Column[int](ForeignKey("main_shopaddress.id"), nullable=False)
    address: Mapped["Address"] = relationship("Address", back_populates="transactions")
