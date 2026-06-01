"""Configuration settings for OpenTelemetry."""

__all__ = ("OpenTelemetry",)

from pydantic import BaseModel, Field


class OpenTelemetry(BaseModel):
    """Pydantic model representing settings for OpenTelemetry.

    This model encapsulates configuration options such as the endpoint for the OpenTelemetry collector.
    """

    endpoint: str | None = Field(
        None,
        description="The endpoint for the OpenTelemetry collector.",
    )
    enable_console: bool = Field(
        False,
        description="Whether to enable console logging for OpenTelemetry.",
    )
