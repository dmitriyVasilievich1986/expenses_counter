"""User model module."""

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from expenses_counter.services.database.models.transaction import Transaction


class User(Base):
    """SQLAlchemy model representing an application user.

    Users authenticate with a username and password; email is stored for
    identification and contact. Each user can own multiple expense transactions.

    Attributes:
        id: Primary key identifier for the user.
        username: Unique login name (max 150 characters, enforced by DB constraint).
        email: Unique email address (max 150 characters, enforced by DB constraint).
        password: Stored password credential (typically a password hash).
        transactions: Related Transaction records for this user.

    """

    __tablename__ = "main_user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(150), nullable=False)

    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="user")
