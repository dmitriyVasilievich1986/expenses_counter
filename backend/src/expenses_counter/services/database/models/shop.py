"""Shop model module."""

__all__ = ("Shop",)

from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, relationship

from .base import Base

if TYPE_CHECKING:
    from expenses_counter.services.database.models.address import Address
    from expenses_counter.services.database.models.category import Category


class Shop(Base):
    """SQLAlchemy model representing a Shop entity.

    Shops represent retail stores or vendors where purchases can be made. Each shop
    can be associated with a category for organizational purposes and can have multiple
    addresses (e.g., different store locations, warehouses).

    Attributes:
        id: Primary key identifier for the shop.
        name: The name of the shop (required, max 150 characters).
        icon: Optional icon representing the shop visually (max 150 characters).
            Can be a URL or icon identifier.
        description: Optional description providing additional details about the shop.
        category_id: Optional foreign key reference to a category that classifies
            this shop. None indicates the shop is not categorized.
        category: Relationship to the Category entity that classifies this shop.
        addresses: Relationship to a list of Address entities associated with this shop.
            A shop can have multiple addresses (e.g., multiple store locations).

    """

    __tablename__ = "main_shop"

    id: int = Column[int](Integer, primary_key=True, autoincrement=True)
    name: str = Column[str](String(150), nullable=False)
    icon: str | None = Column[str | None](String(150), nullable=True)
    description: str | None = Column[str | None](Text, nullable=True)

    addresses: Mapped[list["Address"]] = relationship("Address", back_populates="shop")

    category_id: int | None = Column[int | None](ForeignKey("main_category.id"), nullable=True)
    category: Mapped["Category | None"] = relationship("Category", back_populates="shops")
