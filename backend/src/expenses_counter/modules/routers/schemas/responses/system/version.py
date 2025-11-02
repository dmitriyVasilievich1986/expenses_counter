"""Version response models."""

__all__ = ("VersionResponse",)

from pydantic import Field

from expenses_counter.modules.routers.schemas.base import BaseResponseModel


class VersionResponse(BaseResponseModel):
    """Response model for service version."""

    version: str = Field(
        ...,
        description="Service version",
    )
