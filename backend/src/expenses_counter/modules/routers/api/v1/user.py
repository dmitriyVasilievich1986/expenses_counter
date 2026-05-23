"""User API router module.

REST endpoints for the authenticated user's profile: read current user,
full replace, and partial update.

Routes:
    GET /user/me - Get the current user
    PUT /user - Replace the current user's fields
    PATCH /user - Partially update the current user
    GET /user/available-pages - Page keys the user may access
"""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError

from expenses_counter.modules.middlewares.dependencies import get_db
from expenses_counter.modules.middlewares.dependencies.user_authorized import user_authorized
from expenses_counter.modules.routers.schemas.requests.user import (
    PatchUserBody,
    PutUserBody,
)
from expenses_counter.modules.routers.schemas.responses.user import (
    GetSingleUserResponse,
)
from expenses_counter.services.daos import UserDAO
from expenses_counter.services.database import AsyncDatabaseClient
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
    body: Annotated[PutUserBody, Body(description="The user data to update")],
    user: Annotated[User, Depends(user_authorized)],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleUserResponse:
    """Replace the authenticated user's profile with the request body.

    Args:
        body (PutUserBody): Full replacement payload for the current user.
        user (User): Authenticated user performing the update.
        db (AsyncDatabaseClient): Database client for the request.

    Returns:
        GetSingleUserResponse: The updated user payload.

    Raises:
        HTTPException: 400 if a referenced entity violates integrity.
        HTTPException: 404 if the authenticated user record is missing.
        HTTPException: 500 if a database error occurs while updating the user.

    """
    user_dao = UserDAO(database_client=db)

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
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleUserResponse:
    """Patch the authenticated user's profile.

    Args:
        user (User): Authenticated user performing the update.
        body (PatchUserBody): Partial update payload for the current user.
        db (AsyncDatabaseClient): Database client for the request.

    Returns:
        GetSingleUserResponse: The updated user payload.

    Raises:
        HTTPException: 400 if a referenced entity violates integrity.
        HTTPException: 404 if the authenticated user record is missing.
        HTTPException: 500 if a database error occurs while patching the user.

    """
    user_dao = UserDAO(database_client=db)

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


@router.get(
    "/available-pages",
    response_model=list[str],
    status_code=status.HTTP_200_OK,
    description="Get the available pages",
)
async def get_available_pages(user: Annotated[User, Depends(user_authorized)]) -> list[str]:
    """Return route page identifiers the authenticated user is allowed to open.

    Admin users receive identifiers for admin-only sections; non-admins get an
    empty list.

    Args:
        user (User): The user resolved from the JWT by ``user_authorized``.

    Returns:
        list[str]: Page keys (e.g. ``shops``, ``products``) or an empty list.

    """
    if user.is_admin:
        return ["shops", "products"]

    return []
