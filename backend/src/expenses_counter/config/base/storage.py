"""Settings storage module."""

__all__ = ("SettingsStorage",)

from typing import Optional, TYPE_CHECKING

from expenses_counter.utils import Singleton

if TYPE_CHECKING:
    from .base import BaseConfig


class SettingsStorage(metaclass=Singleton):
    """Thread-safe storage for application settings.

    This class provides a singleton instance for storing configuration settings.
    It ensures only one instance exists across the application and provides
    thread-safe access to the stored settings through property accessors.
    """

    _settings: Optional["BaseConfig"] = None

    @property
    def settings(self) -> Optional["BaseConfig"]:
        """Get the currently stored settings instance.

        Returns:
            Optional[BaseConfig]: The stored settings instance, or None if
                no settings have been set yet.

        """
        return self._settings

    @settings.setter
    def settings(self, settings: "BaseConfig"):
        """Set the settings instance.

        Args:
            settings: The BaseConfig instance to store.

        """
        self._settings = settings

    @settings.deleter
    def settings(self) -> None:
        """Clear the stored settings instance.

        Sets the internal settings storage to None, effectively clearing
        any previously stored configuration.
        """
        self._settings = None
