"""Base config module."""

__all__ = ("BaseConfig",)

from typing import Self

from pydantic_settings import BaseSettings, SettingsConfigDict

from .storage import SettingsStorage


class BaseConfig(BaseSettings):
    """Base configuration class for application settings.

    This class extends Pydantic's BaseSettings to provide a foundation for
    configuration classes. It supports loading settings from .env files with
    nested configuration support and implements a singleton-like pattern
    through the get_or_create class method.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    @classmethod
    def get_or_create(cls, reload: bool = False) -> Self:
        """Get existing settings instance or create a new one.

        This method implements a singleton-like pattern by storing the settings
        instance in SettingsStorage. If an instance already exists and reload
        is False, it returns the existing instance. Otherwise, it creates a new
        instance and stores it.

        Args:
            reload: If True, forces creation of a new settings instance even
                if one already exists. Defaults to False.

        Returns:
            Self: An instance of the configuration class.

        """
        storage = SettingsStorage()

        if not reload and storage.settings:
            return storage.settings

        settings = cls()
        storage.settings = settings
        return settings
