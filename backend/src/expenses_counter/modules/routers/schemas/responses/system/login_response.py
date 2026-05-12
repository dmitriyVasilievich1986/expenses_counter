"""Login response schema module."""

__all__ = ("LoginResponse",)

from datetime import datetime

from pydantic import Field

from expenses_counter.modules.routers.schemas.base import BaseResponseModel


class LoginResponse(BaseResponseModel):
    """Login response schema."""

    access_token: str = Field(..., description="The access token of the user")
    expires_at: datetime = Field(..., description="The expiration date of the token")
