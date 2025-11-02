"""Base schema module."""

__all__ = ("BaseSchema",)

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseSchema(BaseModel):
    """Base schema for all DAOs."""

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        serialize_by_alias=True,
        validate_by_alias=True,
    )
