"""DAO for creating and loading ``User`` records with hashed passwords."""

__all__ = ("UserDAO",)


from typing import Any

from sqlalchemy.sql import ColumnElement

from expenses_counter.services.auth import PasswordService
from expenses_counter.services.daos.base import BaseDAO
from expenses_counter.services.database.models.user import User


class UserDAO(BaseDAO[User]):
    """Persistence helpers for ``User`` rows, including password hashing on create."""

    database_model = User
    get_all_columns = (User.id, User.username, User.email)

    async def get_by_username(self, username: str, filters: list[ColumnElement[bool]] | None = None) -> User:
        """Load one user row by ``username``.

        Uses an injected session when present; otherwise opens a
        short-lived session from the bound database client.

        Args:
            username (str): Value of the ``username`` column to match.
            filters (list[ColumnElement[bool]] | None, optional): Extra WHERE
                clauses merged with ``base_filters``. Defaults to None.

        Returns:
            User: The matching ORM instance.

        """
        if self.session is not None:
            return await self._get_by_pk_raw(self.session, username, "username", filters)

        async with self.database_client.session_factory() as session:  # type: ignore[union-attr]
            return await self._get_by_pk_raw(session, username, "username", filters)

    async def create(self, filters: list[ColumnElement[bool]] | None = None, **kwargs: Any) -> User:
        """Insert a user row with a bcrypt-hashed password.

        Expects a plaintext ``password`` in ``kwargs``; stores the hash on the
        new row. Uses an injected session when present; otherwise opens a
        short-lived session from the bound database client.

        Args:
            filters (list[ColumnElement[bool]] | None, optional): Extra WHERE
                clauses applied during insert. Defaults to None.
            **kwargs (Any): Column values for the new ``User``, including
                ``password`` (plaintext).

        Returns:
            User: The persisted ORM instance.

        """
        hashed_password = PasswordService.hash_password(kwargs["password"])

        if self.session is not None:
            return await self._create_raw(self.session, **(kwargs | {"password": hashed_password}), filters=filters)

        async with self.database_client.session_factory() as session:  # type: ignore[union-attr]
            return await self._create_raw(session, **(kwargs | {"password": hashed_password}), filters=filters)
