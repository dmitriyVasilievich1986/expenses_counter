"""Database connection configuration model.

This module defines the configuration model for database connections, supporting
multiple database providers (SQLite and PostgreSQL) and generating SQLAlchemy
connection URLs.
"""

__all__ = ("Database",)

from typing import Literal

from pydantic import BaseModel, Field, SecretStr
from sqlalchemy.engine import URL


class Database(BaseModel):
    """Configuration model for database connection settings.

    This model handles database connection configuration for different providers,
    including SQLite for local development and PostgreSQL for production. It
    securely manages credentials using Pydantic's SecretStr and generates
    SQLAlchemy connection URLs.

    Attributes:
        provider: The database provider type. Must be either "sqlite" or
            "postgresql". This is a required field.
        host: The database host. For SQLite, this is the file path to the
            database file. For PostgreSQL, this is the hostname or IP address
            of the database server. This is a required field.
        port: The port number for the database connection. Only used for
            PostgreSQL. Defaults to None (uses provider default).
        name: The name of the database. Only used for PostgreSQL. For SQLite,
            the database name is part of the host path. Defaults to None.
        user: The username for database authentication. Only used for
            PostgreSQL. Stored securely as SecretStr. Defaults to None.
        password: The password for database authentication. Only used for
            PostgreSQL. Stored securely as SecretStr. Defaults to None.

    Properties:
        url: Generates a SQLAlchemy URL object for the configured database
            connection.

    Raises:
        ValueError: If an invalid database provider is specified.

    Example:
        SQLite configuration:
        >>> db = Database(provider="sqlite", host="./data.db")
        >>> print(db.url)
        sqlite:///./data.db

        PostgreSQL configuration:
        >>> db = Database(
        ...     provider="postgresql",
        ...     host="localhost",
        ...     port=5432,
        ...     name="expenses_db",
        ...     user=SecretStr("dbuser"),
        ...     password=SecretStr("dbpass")
        ... )

    """

    provider: Literal["sqlite", "postgresql"] = Field(..., description="The provider of the database")
    host: str = Field(..., description="The host of the database")

    port: int | None = Field(None, description="The port of the database")
    name: str | None = Field(None, description="The name of the database")
    user: SecretStr | None = Field(None, description="The user of the database")
    password: SecretStr | None = Field(None, description="The password of the database")

    @property
    def url(self) -> URL:
        """Generate a SQLAlchemy URL for the database connection.

        Creates a SQLAlchemy URL object based on the configured provider and
        connection parameters. For SQLite, only the database file path is used.
        For PostgreSQL, all connection parameters including credentials are
        included.

        Returns:
            URL: A SQLAlchemy URL object that can be used to create database
                engine connections.

        Raises:
            ValueError: If the provider is not "sqlite" or "postgresql".

        """
        if self.provider == "sqlite":
            return URL.create("sqlite", database=self.host)
        if self.provider == "postgresql":
            return URL.create(
                "postgresql",
                username=self.user.get_secret_value(),
                password=self.password.get_secret_value(),
                host=self.host,
                port=self.port,
                database=self.name,
            )
        raise ValueError(f"Invalid database provider: {self.provider}")
