"""Shop model module."""

__all__ = ("Shop",)

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from expenses_counter.services.database.models.address import Address
    from expenses_counter.services.database.models.category import Category


class Shop(Base):
    """SQLAlchemy model representing a shop where purchases can occur.

    Attributes:
        id: Primary key identifier for the shop.
        name: Display name of the shop (required, max 150 characters).
        icon: Optional icon identifier or URL for UI display.
        description: Optional longer description of the shop.
        addresses: Physical or mailing addresses linked to this shop.
        category_id: Optional foreign key to classify the shop under a category.
        category: Related Category entity when category_id is set.

    """

    __tablename__ = "main_shop"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    icon: Mapped[str | None] = mapped_column(String(150), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    addresses: Mapped[list["Address"]] = relationship("Address", back_populates="shop")

    category_id: Mapped[int | None] = mapped_column(ForeignKey("main_category.id"), nullable=True)
    category: Mapped["Category | None"] = relationship("Category", back_populates="shops")
