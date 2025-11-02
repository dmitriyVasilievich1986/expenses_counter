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

    allowed_hosts: list[str] = Field(
        ["*"], description="The allowed hosts to use for the application"
    )

    secret_key: str = Field(
        "secret",
        description="The secret key to use for the application",
        json_schema_extra={"env_shortcut": "SECRET_KEY"},
    )
    debug: bool = Field(
        False,
        description="The debug mode to use for the application",
        json_schema_extra={"env_shortcut": "DEBUG"},
    )

    database_engine: Literal["sqlite", "postgresql"] = Field(
        "sqlite",
        description="The database engine to use",
        json_schema_extra={"env_shortcut": "DATABASE_ENGINE"},
    )
    database_host: str = Field(
        "expenses_counter.sqlite3",
        description="The database host to use",
        json_schema_extra={"env_shortcut": "DATABASE_HOST"},
    )
    database_password: SecretStr | None = Field(
        None,
        description="The database password to use",
        json_schema_extra={"env_shortcut": "DATABASE_PASSWORD"},
    )
    database_user: str | None = Field(
        None,
        description="The database user to use",
        json_schema_extra={"env_shortcut": "DATABASE_USER"},
    )
    database_name: str | None = Field(
        None,
        description="The database name to use",
        json_schema_extra={"env_shortcut": "DATABASE_NAME"},
    )
    database_port: int | None = Field(
        None,
        description="The database port to use",
        json_schema_extra={"env_shortcut": "DATABASE_PORT"},
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
