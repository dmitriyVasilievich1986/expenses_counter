"""Product model module."""

__all__ = ("Product",)

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from expenses_counter.services.database.models.category import Category
    from expenses_counter.services.database.models.transaction import Transaction


class Product(Base):
    """SQLAlchemy model representing a Product entity.

    Products represent individual items or goods that can be purchased from shops.
    Each product belongs to a specific category and can have multiple transactions.

    Attributes:
        id: Primary key identifier for the product.
        name: The name of the product (required, max 150 characters).
        description: Optional description providing additional details about the product.
        sub_category_id: Optional foreign key reference to a category that this product belongs to.
        sub_category: Relationship to the Category entity that this product belongs to.

    """

    __tablename__ = "main_product"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="product")

    category_id: Mapped[int | None] = mapped_column(ForeignKey("main_category.id"), nullable=True)
    category: Mapped["Category | None"] = relationship("Category", back_populates="products")
