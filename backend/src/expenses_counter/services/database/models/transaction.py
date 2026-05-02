"""Transaction model module."""

__all__ = ("Transaction",)

import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from expenses_counter.services.database.models.address import Address
    from expenses_counter.services.database.models.product import Product


class Transaction(Base):
    """SQLAlchemy model representing a single purchase line on a receipt.

    A transaction ties a product, quantity, and price to the address (shop
    location) where the purchase occurred.

    Attributes:
        id: Primary key identifier for the transaction line.
        date: Calendar date when the purchase was made.
        count: Quantity or amount purchased (stored with up to three decimal places).
        price: Monetary value for this line (stored with up to two decimal places).
        product_id: Foreign key to the purchased product.
        product: Related Product entity.
        address_id: Foreign key to the shop address where the purchase occurred.
        address: Related Address entity.

    """

    __tablename__ = "main_transaction"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    count: Mapped[float] = mapped_column(
        Numeric[float](precision=10, scale=3, asdecimal=True), nullable=False, default=0
    )
    price: Mapped[float] = mapped_column(
        Numeric[float](precision=10, scale=2, asdecimal=True), nullable=False, default=0
    )

    product_id: Mapped[int] = mapped_column(ForeignKey("main_product.id"), nullable=False)
    product: Mapped["Product"] = relationship("Product", back_populates="transactions")

    address_id: Mapped[int] = mapped_column(ForeignKey("main_shopaddress.id"), nullable=False)
    address: Mapped["Address"] = relationship("Address", back_populates="transactions")
