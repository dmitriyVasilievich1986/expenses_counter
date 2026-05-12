"""JWT token metadata model."""

__all__ = ("JWTTokenMetadata",)

from datetime import datetime

from pydantic import BaseModel, Field


class JWTTokenMetadata(BaseModel):
    """JWT token metadata model."""

    user_id: int = Field(..., description="The user ID")
    exp: datetime = Field(..., description="The expiration date of the token")
