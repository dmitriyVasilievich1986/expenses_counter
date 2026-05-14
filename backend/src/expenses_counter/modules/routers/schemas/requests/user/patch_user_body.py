"""Patch user body schema module."""

__all__ = ("PatchUserBody",)

from pydantic import Field

from expenses_counter.modules.routers.schemas.base.request import BaseRequestModel


class PatchUserBody(BaseRequestModel):
    """Request body for patching a user."""

    first_name: str | None = Field(None, min_length=1, max_length=150, description="The first name of the user")
    last_name: str | None = Field(None, min_length=1, max_length=150, description="The last name of the user")
    photo_url: str | None = Field(None, max_length=255, description="The photo url of the user")
