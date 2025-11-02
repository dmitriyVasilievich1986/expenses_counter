"""Shop model module."""

__all__ = ("Shop",)

from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, relationship

from .base import Base

if TYPE_CHECKING:
    from expenses_counter.models.category import Category


class Shop(Base):
    __tablename__ = "main_shop"

    id: int = Column[int](Integer, primary_key=True, autoincrement=True)
    name: str = Column[str](String(150), nullable=False)
    icon: str | None = Column[str | None](String(150), nullable=True)
    description: str | None = Column[str | None](Text, nullable=True)

    category_id: int | None = Column[int | None](
        ForeignKey("main_category.id"),
        nullable=True,
    )
    category: Mapped["Category"] = relationship(
        "Category", remote_side=[category_id], back_populates="shops"
    )
