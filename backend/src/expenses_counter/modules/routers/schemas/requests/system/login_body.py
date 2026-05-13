"""Login body schema module."""

__all__ = ("LoginBody",)

from pydantic import Field

from expenses_counter.modules.routers.schemas.base.request import BaseRequestModel


class LoginBody(BaseRequestModel):
    """Login body schema."""

    username: str = Field(..., description="The username of the user")
    password: str = Field(..., description="The password of the user")
