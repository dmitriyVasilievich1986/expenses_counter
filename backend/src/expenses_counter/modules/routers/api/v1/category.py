"""HTTP API routes for expense categories.

Provides list, read, create, update, and delete endpoints for the category
hierarchy (parent/child). List endpoints support pagination and sorting.

Routes:
    GET /category - Paginated list of all categories
    GET /category/parent - Root categories only (no parent)
    GET /category/parent/{parent_id} - Children of a given parent
    GET /category/{category_id} - Single category by id
    POST /category - Create a category
    PUT /category/{category_id} - Replace a category
    DELETE /category/{category_id} - Delete a category
"""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from loguru import logger
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError

from expenses_counter.modules.middlewares.dependencies.admin_required import admin_required
from expenses_counter.modules.middlewares.dependencies.daos import get_category
from expenses_counter.modules.routers.schemas.base.metadata import PaginationMetadata
from expenses_counter.modules.routers.schemas.requests.category import (
    GetAllCategoriesByParentQuery,
    GetAllCategoriesQuery,
    PatchCategoryBody,
    PostCategoryBody,
    PutCategoryBody,
)
from expenses_counter.modules.routers.schemas.responses.category import (
    GetAllCategoriesResponse,
    GetSingleCategoryResponse,
    SimpleCategoryGet,
)
from expenses_counter.services.daos import CategoryDAO
from expenses_counter.utils.filter import Filter

router = APIRouter(prefix="/category", tags=["Category"], dependencies=[Depends(admin_required)])


@router.get("", response_model=GetAllCategoriesResponse, status_code=status.HTTP_200_OK)
async def get_category_list(
    category_dao: Annotated[CategoryDAO, Depends(get_category)],
    query: Annotated[GetAllCategoriesQuery, Query(description="Pagination and sorting parameters")],
) -> GetAllCategoriesResponse:
    """Return all categories with pagination metadata.

    Args:
        category_dao (CategoryDAO): Category data access object.
        query (GetAllCategoriesQuery): Pagination and sort parameters.

    Returns:
        GetAllCategoriesResponse: Categories and pagination metadata.

    Raises:
        HTTPException: 500 if a database error occurs while listing categories.

    """
    try:
        data, total = await category_dao.get_all(**query.model_dump())
        metadata = PaginationMetadata(total=total, **query.model_dump())
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while retrieving the category list", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while retrieving the category list",
        ) from e

    return GetAllCategoriesResponse(
        data=[SimpleCategoryGet.model_validate(category) for category in data], metadata=metadata
    )


@router.get("/parent", response_model=GetAllCategoriesResponse, status_code=status.HTTP_200_OK, deprecated=True)
async def get_root_category_list(
    category_dao: Annotated[CategoryDAO, Depends(get_category)],
    query: Annotated[GetAllCategoriesByParentQuery, Query(description="Pagination and sorting parameters")],
) -> GetAllCategoriesResponse:
    """Return top-level categories (those with no parent).

    Args:
        category_dao (CategoryDAO): Category data access object.
        query (GetAllCategoriesByParentQuery): Pagination and sort parameters.

    Returns:
        GetAllCategoriesResponse: Root categories and pagination metadata.

    Raises:
        HTTPException: 500 if a database error occurs while listing categories.

    """
    try:
        filters = [Filter[str](column="parent_id", operator="isnull", value=None)]
        data, total = await category_dao.get_all(filters=[f.model_dump() for f in filters], **query.model_dump())
        metadata = PaginationMetadata(total=total, **query.model_dump(), filters=filters)
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while retrieving the category list by parent", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while retrieving the category list by parent",
        ) from e

    return GetAllCategoriesResponse(
        data=[SimpleCategoryGet.model_validate(category) for category in data], metadata=metadata
    )


@router.get(
    "/parent/{parent_id}", response_model=GetAllCategoriesResponse, status_code=status.HTTP_200_OK, deprecated=True
)
async def get_category_list_by_parent(
    parent_id: Annotated[int, Path(description="The unique identifier of the parent category to retrieve")],
    category_dao: Annotated[CategoryDAO, Depends(get_category)],
    query: Annotated[GetAllCategoriesByParentQuery, Query(description="Pagination and sorting parameters")],
) -> GetAllCategoriesResponse:
    """Return direct child categories of the given parent.

    Args:
        parent_id (int): Parent category primary key.
        category_dao (CategoryDAO): Category data access object.
        query (GetAllCategoriesByParentQuery): Pagination and sort parameters.

    Returns:
        GetAllCategoriesResponse: Child categories and pagination metadata.

    Raises:
        HTTPException: 500 if a database error occurs while listing categories.

    """
    try:
        filters = [Filter[str](column="parent_id", operator="eq", value=parent_id)]
        data, total = await category_dao.get_all(filters=[f.model_dump() for f in filters], **query.model_dump())
        metadata = PaginationMetadata(total=total, **query.model_dump(), filters=filters)
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while retrieving the category list by parent", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while retrieving the category list by parent",
        ) from e

    return GetAllCategoriesResponse(
        data=[SimpleCategoryGet.model_validate(category) for category in data], metadata=metadata
    )


@router.get(
    "/{category_id}",
    response_model=GetSingleCategoryResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(admin_required)],
)
async def get_category_by_id(
    category_id: Annotated[int, Path(description="The unique identifier of the category to retrieve")],
    category_dao: Annotated[CategoryDAO, Depends(get_category)],
) -> GetSingleCategoryResponse:
    """Return a single category by primary key.

    Args:
        category_id (int): Category primary key.
        category_dao (CategoryDAO): Category data access object.

    Returns:
        GetSingleCategoryResponse: The requested category payload.

    Raises:
        HTTPException: 404 if no category exists for ``category_id``.
        HTTPException: 500 if a database error occurs while loading the category.

    """
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
    dependencies=[Depends(admin_required)],
)
async def create_category(
    body: Annotated[PostCategoryBody, Body(description="The category data to create")],
    category_dao: Annotated[CategoryDAO, Depends(get_category)],
) -> GetSingleCategoryResponse:
    """Create a new category from the request body.

    Args:
        body (PostCategoryBody): Fields for the new category.
        category_dao (CategoryDAO): Category data access object.

    Returns:
        GetSingleCategoryResponse: The created category.

    Raises:
        HTTPException: 400 if a referenced parent or related row violates integrity.
        HTTPException: 500 if a database error occurs while creating the category.

    """
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
    dependencies=[Depends(admin_required)],
)
async def update_category(
    category_id: Annotated[int, Path(description="The unique identifier of the category to update")],
    body: Annotated[PutCategoryBody, Body(description="The category data to update")],
    category_dao: Annotated[CategoryDAO, Depends(get_category)],
) -> GetSingleCategoryResponse:
    """Replace an existing category with the request body.

    Args:
        category_id (int): Category primary key to update.
        body (PutCategoryBody): Full replacement payload.
        category_dao (CategoryDAO): Category data access object.

    Returns:
        GetSingleCategoryResponse: The updated category.

    Raises:
        HTTPException: 404 if no category exists for ``category_id``.
        HTTPException: 400 if a referenced parent or related row violates integrity.
        HTTPException: 500 if a database error occurs while updating the category.

    """
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
    dependencies=[Depends(admin_required)],
)
async def patch_category(
    category_id: Annotated[int, Path(description="The unique identifier of the category to update")],
    body: Annotated[PatchCategoryBody, Body(description="The category data to update")],
    category_dao: Annotated[CategoryDAO, Depends(get_category)],
) -> GetSingleCategoryResponse:
    """Update an existing category with the request body.

    Args:
        category_id (int): Category primary key to update.
        body (PatchCategoryBody): Partial update payload.
        category_dao (CategoryDAO): Category data access object.

    Returns:
        GetSingleCategoryResponse: The updated category.

    Raises:
        HTTPException: 404 if no category exists for ``category_id``.
        HTTPException: 400 if a referenced parent or related row violates integrity.
        HTTPException: 500 if a database error occurs while updating the category.

    """
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


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(admin_required)])
async def delete_category(
    category_id: Annotated[int, Path(description="The unique identifier of the category to delete")],
    category_dao: Annotated[CategoryDAO, Depends(get_category)],
) -> None:
    """Delete a category by primary key.

    Args:
        category_id (int): Category primary key to delete.
        category_dao (CategoryDAO): Category data access object.

    Returns:
        None

    Raises:
        HTTPException: 404 if no category exists for ``category_id``.
        HTTPException: 500 if a database error occurs while deleting the category.

    """
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
