"""Address model module."""

__all__ = ("Address",)

from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

from .base import Base

if TYPE_CHECKING:
    from expenses_counter.services.database.models.shop import Shop
    from expenses_counter.services.database.models.transaction import Transaction


class Address(Base):
    """SQLAlchemy model representing an Address entity.

    Addresses represent physical locations associated with shops. Each address
    belongs to a specific shop and contains location information such as a
    local name (e.g., "Main Store", "Warehouse") and the actual address string.

    Attributes:
        id: Primary key identifier for the address.
        local_name: The local name or identifier for this address location
            (required, max 150 characters). Examples: "Headquarters", "Branch 1".
        address: The physical address string (required, max 150 characters).
            Contains the street address, city, or other location details.
        shop_id: Foreign key reference to the shop that owns this address
            (required).
        shop: Relationship to the Shop entity that this address belongs to.

    """

    __tablename__ = "main_shopaddress"

    id: int = Column[int](Integer, primary_key=True, autoincrement=True)
    local_name: str = Column[str](String(150), nullable=False)
    address: str = Column[str](String(150), nullable=False)

    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="address")

    shop_id: int = Column[int](ForeignKey("main_shop.id"), nullable=False)
    shop: Mapped["Shop"] = relationship("Shop", remote_side=[shop_id])
