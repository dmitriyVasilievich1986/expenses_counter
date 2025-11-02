"""Unhealth response models."""

__all__ = ("UnhealthResponse",)

from pydantic import Field

from expenses_counter.modules.routers.schemas.base import BaseResponseModel


class UnhealthResponse(BaseResponseModel):
    """Response model for unhealth messages."""

    detail: str = Field(
        ...,
        description="Unhealth detail message.",
    )
