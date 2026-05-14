"""User API router module.

REST endpoints for the authenticated user's profile: read current user,
full replace, and partial update.

Routes:
    GET /user/me - Get the current user
    PUT /user - Replace the current user's fields
    PATCH /user - Partially update the current user
"""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError

from expenses_counter.modules.middlewares.dependencies.daos.user_dao import get_user_dao
from expenses_counter.modules.middlewares.dependencies.user_authorized import user_authorized
from expenses_counter.modules.routers.schemas.requests.user import (
    PatchUserBody,
    PutUserBody,
)
from expenses_counter.modules.routers.schemas.responses.user import (
    GetSingleUserResponse,
)
from expenses_counter.services.daos import UserDAO
from expenses_counter.services.database.models.user import User

router = APIRouter(prefix="/user", tags=["User"])


@router.get(
    "/me",
    response_model=GetSingleUserResponse,
    status_code=status.HTTP_200_OK,
    description="Get the current user",
)
async def me(user: Annotated[User, Depends(user_authorized)]) -> GetSingleUserResponse:
    """Return the authenticated user's profile.

    Args:
        user (User): The user resolved from the JWT by ``user_authorized``.

    Returns:
        GetSingleUserResponse: Serializable user record for the client.

    """
    return GetSingleUserResponse.model_validate(user)


@router.put(
    "",
    response_model=GetSingleUserResponse,
    status_code=status.HTTP_200_OK,
    description="Update the current user",
)
async def update_me(
    user: Annotated[User, Depends(user_authorized)],
    body: Annotated[PutUserBody, Body(description="The user data to update")],
    user_dao: Annotated[UserDAO, Depends(get_user_dao)],
) -> GetSingleUserResponse:
    """Replace the authenticated user's editable fields.

    Args:
        user (User): The user resolved from the JWT by ``user_authorized``.
        body (PutUserBody): Full payload of fields to persist.
        user_dao (UserDAO): DAO used to persist the update.

    Returns:
        GetSingleUserResponse: Updated user as returned by the persistence layer.

    Raises:
        HTTPException: If the user is missing (404), an integrity constraint
            fails (400), or another database error occurs (500).

    """
    try:
        payload = await user_dao.update(user.id, **body.model_dump())
    except NoResultFound as e:
        logger.warning("User not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found") from e
    except IntegrityError as e:
        logger.exception("Related object not found", exc_info=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related object not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while updating the user", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while updating the user",
        ) from e

    return GetSingleUserResponse.model_validate(payload)


@router.patch(
    "",
    response_model=GetSingleUserResponse,
    status_code=status.HTTP_200_OK,
    description="Patch the current user",
)
async def patch_me(
    user: Annotated[User, Depends(user_authorized)],
    body: Annotated[PatchUserBody, Body(description="The user data to patch")],
    user_dao: Annotated[UserDAO, Depends(get_user_dao)],
) -> GetSingleUserResponse:
    """Apply a partial update to the authenticated user's fields.

    Args:
        user (User): The user resolved from the JWT by ``user_authorized``.
        body (PatchUserBody): Only fields present in the request body are updated.
        user_dao (UserDAO): DAO used to persist the patch.

    Returns:
        GetSingleUserResponse: Updated user as returned by the persistence layer.

    Raises:
        HTTPException: If the user is missing (404), an integrity constraint
            fails (400), or another database error occurs (500).

    """
    try:
        payload = await user_dao.update(user.id, **body.model_dump(exclude_unset=True))
    except NoResultFound as e:
        logger.warning("User not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found") from e
    except IntegrityError as e:
        logger.exception("Related object not found", exc_info=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related object not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while patching the user", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while patching the user",
        ) from e

    return GetSingleUserResponse.model_validate(payload)
