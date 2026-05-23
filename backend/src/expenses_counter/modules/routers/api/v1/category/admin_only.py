"""Admin-only HTTP API routes for expense categories.

Provides read, create, update, and delete endpoints for categories.
Admin access is enforced on the router via ``admin_required``. The
paginated list endpoint lives in ``all_users``.

Routes:
    GET /category/{category_id} - Single category by id
    POST /category - Create a category
    PUT /category/{category_id} - Replace a category
    PATCH /category/{category_id} - Partially update a category
    DELETE /category/{category_id} - Delete a category
"""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from loguru import logger
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError

from expenses_counter.modules.middlewares.dependencies import get_db
from expenses_counter.modules.middlewares.dependencies.admin_required import admin_required
from expenses_counter.modules.routers.schemas.requests.category import (
    PatchCategoryBody,
    PostCategoryBody,
    PutCategoryBody,
)
from expenses_counter.modules.routers.schemas.responses.category import (
    GetSingleCategoryResponse,
)
from expenses_counter.services.daos import CategoryDAO
from expenses_counter.services.database import AsyncDatabaseClient

router = APIRouter(prefix="/category", dependencies=[Depends(admin_required)])


@router.get(
    "/{category_id}",
    response_model=GetSingleCategoryResponse,
    status_code=status.HTTP_200_OK,
)
async def get_category_by_id(
    category_id: Annotated[int, Path(description="The unique identifier of the category to retrieve")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleCategoryResponse:
    """Return a single category by primary key.

    Args:
        category_id (int): Category primary key.
        db (AsyncDatabaseClient): Database client for the request.

    Returns:
        GetSingleCategoryResponse: The requested category payload.

    Raises:
        HTTPException: 404 if no category exists for ``category_id``.
        HTTPException: 500 if a database error occurs while loading the category.

    """
    category_dao = CategoryDAO(database_client=db)

    try:
        payload = await category_dao.get_by_pk(category_id)
    except NoResultFound as e:
        logger.warning("Category not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while retrieving the category", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while retrieving the category",
        ) from e

    return GetSingleCategoryResponse.model_validate(payload)


@router.post(
    "",
    response_model=GetSingleCategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    body: Annotated[PostCategoryBody, Body(description="The category data to create")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleCategoryResponse:
    """Create a new category.

    Args:
        body (PostCategoryBody): Fields for the new category (e.g. parent link).
        db (AsyncDatabaseClient): Database client for the request.

    Returns:
        GetSingleCategoryResponse: The created category payload.

    Raises:
        HTTPException: 400 if a referenced entity violates integrity (e.g. missing parent).
        HTTPException: 500 if a database error occurs while creating the category.

    """
    category_dao = CategoryDAO(database_client=db)

    try:
        payload = await category_dao.create(**body.model_dump())
    except IntegrityError as e:
        logger.exception("Related object not found", exc_info=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related object not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while creating the category", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong while creating the category"
        ) from e

    return GetSingleCategoryResponse.model_validate(payload)


@router.put(
    "/{category_id}",
    response_model=GetSingleCategoryResponse,
    status_code=status.HTTP_200_OK,
)
async def update_category(
    category_id: Annotated[int, Path(description="The unique identifier of the category to update")],
    body: Annotated[PutCategoryBody, Body(description="The category data to update")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleCategoryResponse:
    """Replace an existing category by primary key.

    Args:
        category_id (int): Category primary key.
        body (PutCategoryBody): Full replacement payload for the category.
        db (AsyncDatabaseClient): Database client for the request.

    Returns:
        GetSingleCategoryResponse: The updated category payload.

    Raises:
        HTTPException: 400 if a referenced entity violates integrity (e.g. invalid parent).
        HTTPException: 404 if no category exists for ``category_id``.
        HTTPException: 500 if a database error occurs while updating the category.

    """
    category_dao = CategoryDAO(database_client=db)

    try:
        payload = await category_dao.update(category_id, **body.model_dump())
    except NoResultFound as e:
        logger.warning("Category not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found") from e
    except IntegrityError as e:
        logger.exception("Related object not found", exc_info=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related object not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while updating the category", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong while updating the category"
        ) from e

    return GetSingleCategoryResponse.model_validate(payload)


@router.patch(
    "/{category_id}",
    response_model=GetSingleCategoryResponse,
    status_code=status.HTTP_200_OK,
)
async def patch_category(
    category_id: Annotated[int, Path(description="The unique identifier of the category to update")],
    body: Annotated[PatchCategoryBody, Body(description="The category data to update")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleCategoryResponse:
    """Patch an existing category by primary key.

    Args:
        category_id (int): Category primary key.
        body (PatchCategoryBody): Partial update payload for the category.
        db (AsyncDatabaseClient): Database client for the request.

    Returns:
        GetSingleCategoryResponse: The updated category payload.

    Raises:
        HTTPException: 400 if a referenced entity violates integrity (e.g. invalid parent).
        HTTPException: 404 if no category exists for ``category_id``.
        HTTPException: 500 if a database error occurs while patching the category.

    """
    category_dao = CategoryDAO(database_client=db)

    try:
        payload = await category_dao.update(category_id, **body.model_dump(exclude_unset=True))
    except NoResultFound as e:
        logger.warning("Category not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found") from e
    except IntegrityError as e:
        logger.exception("Related object not found", exc_info=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related object not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while patching the category", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong while patching the category"
        ) from e

    return GetSingleCategoryResponse.model_validate(payload)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: Annotated[int, Path(description="The unique identifier of the category to delete")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> None:
    """Delete a category by primary key.

    Args:
        category_id (int): Category primary key.
        db (AsyncDatabaseClient): Database client for the request.

    Returns:
        None

    Raises:
        HTTPException: 404 if no category exists for ``category_id``.
        HTTPException: 500 if a database error occurs while deleting the category.

    """
    category_dao = CategoryDAO(database_client=db)

    try:
        await category_dao.delete(category_id)
    except NoResultFound as e:
        logger.warning("Category not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while deleting the category", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong while deleting the category"
        ) from e
