"""Me response schema module."""

__all__ = ("GetSingleUserResponse",)

from pydantic import Field

from expenses_counter.modules.routers.schemas.base.response import BaseResponseFromModelSchema


class GetSingleUserResponse(BaseResponseFromModelSchema):
    """Response schema for the get single user endpoint."""

    id: int = Field(..., description="The user id")
    username: str = Field(..., description="The username")
    email: str = Field(..., description="The email")
    first_name: str | None = Field(..., description="The first name")
    last_name: str | None = Field(..., description="The last name")
    photo_url: str | None = Field(..., description="The photo url")
    is_active: bool = Field(..., description="Whether the user is active")
