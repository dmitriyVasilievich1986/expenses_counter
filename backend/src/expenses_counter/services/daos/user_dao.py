"""User DAO module."""

__all__ = ("UserDAO",)


from expenses_counter.config import AppConfig
from expenses_counter.services.auth import PasswordService
from expenses_counter.services.daos.base import BaseDAO
from expenses_counter.services.database.models.user import User


class UserDAO(BaseDAO[User]):
    """Data access for ``User`` model."""

    database_model = User
    get_all_columns = (User.id, User.username, User.email)

    async def get_by_username(self, username: str) -> User:
        """Get a user by their username."""
        return await self.get_by_pk(username, "username")

    async def create(self, **kwargs) -> User:
        """Create a row from keyword arguments matching the model fields."""
        app_config = AppConfig.get_or_create()
        password_service = PasswordService(app_config.services.auth.password_secret_key.get_secret_value())
        hashed_password = password_service.hash_password(kwargs["password"])

        if self.session is not None:
            return await self._create_raw(self.session, **(kwargs | {"password": hashed_password}))

        async with self.database_client.session_factory() as session:  # type: ignore[union-attr]
            return await self._create_raw(session, **(kwargs | {"password": hashed_password}))
