"""HTTP endpoints for the authenticated user's profile."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from expenses_counter.modules.middlewares.dependencies.user_authorized import user_authorized
from expenses_counter.modules.routers.schemas.responses.system import (
    MeResponse,
)
from expenses_counter.services.database.models.user import User

router = APIRouter()


@router.get("/me", response_model=MeResponse, status_code=status.HTTP_200_OK, description="Get the current user")
async def me(user: Annotated[User, Depends(user_authorized)]) -> MeResponse:
    """Return profile information for the currently authenticated user.

    Args:
        user (User): The user resolved from the JWT by ``user_authorized``.

    Returns:
        MeResponse: Serializable representation of the user for the client.

    """
    return MeResponse.model_validate(user)
