"""Category model module."""

__all__ = ("Category",)


from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, relationship

from .base import Base

if TYPE_CHECKING:
    from expenses_counter.services.database.models.product import Product
    from expenses_counter.services.database.models.shop import Shop


class Category(Base):
    """SQLAlchemy model representing a Category entity.

    Categories can be organized hierarchically with parent-child relationships.
    This allows for nested categorization structures (e.g., Food -> Fruits -> Apples).

    Attributes:
        id: Primary key identifier for the category.
        name: The name of the category (required, max 150 characters).
        description: Optional description providing additional details about the category.
        parent_id: Optional foreign key reference to a parent category, enabling
            hierarchical category structures. None indicates a top-level category.
        parent: Relationship to the parent Category, if one exists.

    """

    __tablename__ = "main_category"

    id: int = Column[int](Integer, primary_key=True, autoincrement=True)
    name: str = Column[str](String(150), nullable=False)
    description: str | None = Column[str | None](Text, nullable=True)

    shops: Mapped[list["Shop"]] = relationship("Shop", back_populates="category")
    products: Mapped[list["Product"]] = relationship("Product", back_populates="category")

    parent_id: int | None = Column[int | None](ForeignKey("main_category.id"), nullable=True)
    parent: Mapped["Category | None"] = relationship("Category", remote_side=[id], back_populates="children")
    children: Mapped[list["Category"]] = relationship("Category", back_populates="parent")

    @property
    def full_name(self) -> str:
        """Get the full hierarchical name of the category.

        In Python, this recursively builds the name by traversing parents.
        At the SQL level, this returns just the name (recursive CTEs would be needed for full hierarchy).
        """
        payload = self.name
        if self.parent:
            payload = f"{self.parent.full_name} / {payload}"

        return payload
