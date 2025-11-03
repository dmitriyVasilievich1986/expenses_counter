"""App config module."""

__all__ = ("AppConfig",)

from typing import Literal

from pydantic import Field, SecretStr

from .base import BaseConfig


class AppConfig(BaseConfig):
    """Application configuration settings.

    This class holds all application-level configuration settings including
    allowed hosts, secret key, debug mode, and database connection settings.
    Supports both SQLite and PostgreSQL database engines.
    """

    allowed_hosts: list[str] = Field(["*"], description="The allowed hosts to use for the application")
    name: str = Field(
        "Expenses Counter",
        description="The name of the application",
    )
    description: str = Field(
        "The program for counting expenses",
        description="The description of the application",
    )
    app_port: int = Field(
        8000,
        description="The port to use for the application",
    )
    app_log_level: str = Field(
        "INFO",
        description="The log level to use for the application",
    )

    secret_key: str = Field(
        "secret",
        description="The secret key to use for the application",
    )
    debug: bool = Field(
        False,
        description="The debug mode to use for the application",
    )

    database_engine: Literal["sqlite", "postgresql"] = Field(
        "sqlite",
        description="The database engine to use",
    )
    database_host: str = Field(
        "expenses_counter.sqlite3",
        description="The database host to use",
    )
    database_password: SecretStr | None = Field(
        None,
        description="The database password to use",
    )
    database_user: str | None = Field(
        None,
        description="The database user to use",
    )
    database_name: str | None = Field(
        None,
        description="The database name to use",
    )
    database_port: int | None = Field(
        None,
        description="The database port to use",
    )

    @property
    def sqlalchemy_url(self) -> str:
        """Generate SQLAlchemy database URL based on configured database engine.

        Returns:
            str: A SQLAlchemy-compatible database URL string. Format depends on
                the configured database engine:
                - For SQLite: "sqlite+aiosqlite:///{database_host}"
                - For PostgreSQL: "postgresql+psycopg://{user}:{password}:{host}:{port}/{name}"

        """
        match self.database_engine:
            case "sqlite":
                return f"sqlite+aiosqlite:///{self.database_host}"
            case "postgresql":
                return f"postgresql+psycopg://{self.database_user}:{self.database_password}:{self.database_host}:{self.database_port}/{self.database_name}"
