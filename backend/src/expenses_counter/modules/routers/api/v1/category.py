"""Category API router module.

This module provides REST API endpoints for managing categories in the expenses
counter application. It includes full CRUD (Create, Read, Update, Delete) operations
for categories with support for hierarchical category relationships.

The router handles:
    - Listing categories with pagination and sorting
    - Listing categories filtered by parent (including root categories)
    - Retrieving individual categories with parent hierarchy
    - Creating new categories with optional parent relationships
    - Updating existing categories
    - Deleting categories

All endpoints include proper error handling for database exceptions and return
appropriate HTTP status codes.

Routes:
    GET /category - List all categories with pagination
    GET /category/parent - List root categories (categories without a parent)
    GET /category/parent/{parent_id} - List child categories of a specific parent
    GET /category/{category_id} - Get a single category by ID
    POST /category - Create a new category
    PUT /category/{category_id} - Update an existing category
    DELETE /category/{category_id} - Delete a category
"""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from expenses_counter.modules.middlewares.dependencies import get_category
from expenses_counter.modules.routers.schemas.base.metadata import PaginationMetadata
from expenses_counter.modules.routers.schemas.requests.category import (
    GetAllCategoriesQuery,
    PostCategoryBody,
    PutCategoryBody,
)
from expenses_counter.modules.routers.schemas.responses.category import (
    GetAllCategoriesResponse,
    GetSingleCategoryResponse,
    SimpleCategoryGet,
)
from expenses_counter.services.daos import CategoryDAO
from expenses_counter.services.daos.base.exceptions import DBException, NotFoundException, RelationshipNotFoundException

router = APIRouter(prefix="/category", tags=["Category"])


@router.get("", response_model=GetAllCategoriesResponse)
async def get_category_list(
    category_dao: Annotated[CategoryDAO, Depends(get_category)],
    query: Annotated[GetAllCategoriesQuery, Query(description="Pagination and sorting parameters")],
):
    """Retrieve a paginated list of all categories.

    This endpoint returns a list of categories with pagination support, including
    metadata about the total count and pagination parameters. Categories are returned
    with limited fields (id and name) for performance optimization.

    Args:
        category_dao: The category DAO instance for database operations.
            Injected via FastAPI dependency injection.
        query: Query parameters for pagination and sorting, including:
            - limit: Maximum number of categories to return
            - offset: Number of categories to skip
            - sort_by: Field name to sort by
            - sort_order: Sort direction (asc or desc)

    Returns:
        GetAllCategoriesResponse: A response object containing:
            - data: List of category objects with id and name
            - metadata: Pagination information (total, offset, limit, sort parameters)

    Raises:
        HTTPException: 500 Internal Server Error if database operation fails.

    Example:
        GET /category?limit=20&offset=0&sort_by=name&sort_order=asc

    """
    try:
        data, total = await category_dao.get_all(
            limit=query.limit, offset=query.offset, sort_by=query.sort_by, sort_order=query.sort_order
        )
        metadata = PaginationMetadata(
            total=total, offset=query.offset, limit=query.limit, sort_by=query.sort_by, sort_order=query.sort_order
        )
    except DBException as e:
        raise HTTPException(status_code=500, detail="Something went wrong while retrieving the category list") from e

    return GetAllCategoriesResponse(
        data=[SimpleCategoryGet.model_validate(category) for category in data], metadata=metadata
    )


@router.get("/parent", response_model=GetAllCategoriesResponse)
async def get_root_category_list(
    category_dao: Annotated[CategoryDAO, Depends(get_category)],
    query: Annotated[GetAllCategoriesQuery, Query(description="Pagination and sorting parameters")],
):
    """Retrieve a paginated list of root categories (categories without a parent).

    This endpoint returns a list of top-level categories that have no parent category,
    effectively retrieving all root nodes in the category hierarchy. Results include
    pagination support and metadata about the total count.

    Args:
        category_dao: The category DAO instance for database operations.
            Injected via FastAPI dependency injection.
        query: Query parameters for pagination and sorting, including:
            - limit: Maximum number of categories to return
            - offset: Number of categories to skip
            - sort_by: Field name to sort by
            - sort_order: Sort direction (asc or desc)

    Returns:
        GetAllCategoriesResponse: A response object containing:
            - data: List of root category objects with id and name
            - metadata: Pagination information (total, offset, limit, sort parameters)

    Raises:
        HTTPException: 500 Internal Server Error if database operation fails.

    Example:
        GET /category/parent?limit=20&offset=0&sort_by=name&sort_order=asc

    """
    try:
        data, total = await category_dao.get_all_by_parent(
            None, limit=query.limit, offset=query.offset, sort_by=query.sort_by, sort_order=query.sort_order
        )
        metadata = PaginationMetadata(
            total=total, offset=query.offset, limit=query.limit, sort_by=query.sort_by, sort_order=query.sort_order
        )
    except DBException as e:
        raise HTTPException(
            status_code=500, detail="Something went wrong while retrieving the category list by parent"
        ) from e

    return GetAllCategoriesResponse(
        data=[SimpleCategoryGet.model_validate(category) for category in data], metadata=metadata
    )


@router.get("/parent/{parent_id}", response_model=GetAllCategoriesResponse)
async def get_category_list_by_parent(
    parent_id: Annotated[int, Path(description="The unique identifier of the parent category to retrieve")],
    category_dao: Annotated[CategoryDAO, Depends(get_category)],
    query: Annotated[GetAllCategoriesQuery, Query(description="Pagination and sorting parameters")],
):
    """Retrieve a paginated list of child categories for a specific parent category.

    This endpoint returns all categories that are direct children of the specified
    parent category. This is useful for building hierarchical category trees or
    displaying subcategories. Results include pagination support and metadata.

    Args:
        parent_id: The unique identifier (primary key) of the parent category whose
            children should be retrieved. Must be a positive integer. Provided as a
            path parameter.
        category_dao: The category DAO instance for database operations.
            Injected via FastAPI dependency injection.
        query: Query parameters for pagination and sorting, including:
            - limit: Maximum number of categories to return
            - offset: Number of categories to skip
            - sort_by: Field name to sort by
            - sort_order: Sort direction (asc or desc)

    Returns:
        GetAllCategoriesResponse: A response object containing:
            - data: List of child category objects with id and name
            - metadata: Pagination information (total, offset, limit, sort parameters)

    Raises:
        HTTPException: 500 Internal Server Error if database operation fails.

    Example:
        GET /category/parent/42?limit=20&offset=0&sort_by=name&sort_order=asc

    Note:
        If the parent_id does not exist, an empty list will be returned rather than
        an error, as having no children is a valid state.

    """
    try:
        data, total = await category_dao.get_all_by_parent(
            parent_id, limit=query.limit, offset=query.offset, sort_by=query.sort_by, sort_order=query.sort_order
        )
        metadata = PaginationMetadata(
            total=total, offset=query.offset, limit=query.limit, sort_by=query.sort_by, sort_order=query.sort_order
        )
    except DBException as e:
        raise HTTPException(
            status_code=500, detail="Something went wrong while retrieving the category list by parent"
        ) from e

    return GetAllCategoriesResponse(
        data=[SimpleCategoryGet.model_validate(category) for category in data], metadata=metadata
    )


@router.get("/{category_id}", response_model=GetSingleCategoryResponse)
async def get_category_by_id(
    category_id: Annotated[int, Path(description="The unique identifier of the category to retrieve")],
    category_dao: Annotated[CategoryDAO, Depends(get_category)],
):
    """Retrieve a single category by its unique identifier.

    This endpoint returns detailed information about a specific category, including
    its complete parent hierarchy loaded recursively. This allows clients to display
    the full category path from root to the requested category.

    Args:
        category_id: The unique identifier (primary key) of the category to retrieve.
            Must be a positive integer. Provided as a path parameter.
        category_dao: The category DAO instance for database operations.
            Injected via FastAPI dependency injection.

    Returns:
        GetSingleCategoryResponse: A response object containing the complete category
            information including all parent relationships loaded recursively.

    Raises:
        HTTPException: 404 Not Found if the category with the given ID does not exist.
        HTTPException: 500 Internal Server Error if database operation fails.

    Example:
        GET /category/42

    """
    try:
        category = await category_dao.get_by_id(category_id)
    except DBException as e:
        raise HTTPException(status_code=500, detail="Something went wrong while retrieving the category") from e

    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    return GetSingleCategoryResponse.model_validate(category)


@router.post("", response_model=GetSingleCategoryResponse)
async def create_category(
    body: PostCategoryBody,
    category_dao: Annotated[CategoryDAO, Depends(get_category)],
):
    """Create a new category.

    This endpoint creates a new category with the provided data. Categories can
    optionally have a parent category to establish hierarchical relationships.
    If a parent_id is provided, it must reference an existing category.

    Args:
        body: The category data for creation, including:
            - name: The name of the new category (required)
            - parent_id: Optional ID of the parent category for hierarchy
            - Additional fields as defined in PostCategoryBody schema
        category_dao: The category DAO instance for database operations.
            Injected via FastAPI dependency injection.

    Returns:
        GetSingleCategoryResponse: A response object containing the newly created
            category with all its fields, including the assigned ID and any loaded
            parent relationships.

    Raises:
        HTTPException: 400 Bad Request if the parent category ID is invalid or
            does not exist.
        HTTPException: 500 Internal Server Error if database operation fails.

    Example:
        POST /category
        Body: {"name": "Electronics", "parent_id": 5}

    """
    try:
        payload = await category_dao.create(**body.model_dump(by_alias=False))
    except RelationshipNotFoundException as e:
        raise HTTPException(status_code=400, detail="Parent category not found") from e
    except DBException as e:
        raise HTTPException(status_code=500, detail="There was an error creating the category") from e

    return GetSingleCategoryResponse.model_validate(payload)


@router.put("/{category_id}", response_model=GetSingleCategoryResponse)
async def update_category(
    category_id: Annotated[int, Path(description="The unique identifier of the category to update")],
    body: PutCategoryBody,
    category_dao: Annotated[CategoryDAO, Depends(get_category)],
):
    """Update an existing category by replacing all its fields.

    This endpoint performs a full update (PUT) of a category, replacing all fields
    with the provided data. The category must exist, and if a parent_id is provided,
    the parent category must also exist.

    Args:
        category_id: The unique identifier (primary key) of the category to update.
            Must be a positive integer. Provided as a path parameter.
        body: The complete category data to replace the existing category, including:
            - name: The updated name of the category
            - parent_id: Optional updated parent category ID for hierarchy
            - Additional fields as defined in PutCategoryBody schema
        category_dao: The category DAO instance for database operations.
            Injected via FastAPI dependency injection.

    Returns:
        GetSingleCategoryResponse: A response object containing the updated category
            with all its fields and loaded parent relationships.

    Raises:
        HTTPException: 404 Not Found if the category with the given ID does not exist.
        HTTPException: 400 Bad Request if the parent category ID is invalid or
            does not exist.
        HTTPException: 500 Internal Server Error if database operation fails.

    Example:
        PUT /category/42
        Body: {"name": "Updated Electronics", "parent_id": 3}

    """
    try:
        payload = await category_dao.update(category_id, **body.model_dump(by_alias=False))
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail="Category not found") from e
    except RelationshipNotFoundException as e:
        raise HTTPException(status_code=400, detail="Parent category not found") from e
    except DBException as e:
        raise HTTPException(status_code=500, detail="There was an error updating the category") from e

    return GetSingleCategoryResponse.model_validate(payload)


@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: Annotated[int, Path(description="The unique identifier of the category to delete")],
    category_dao: Annotated[CategoryDAO, Depends(get_category)],
):
    """Delete a category by its unique identifier.

    This endpoint permanently deletes a category from the database. The operation
    will fail if the category has dependent relationships (e.g., child categories
    or associated transactions) that would violate foreign key constraints.

    Args:
        category_id: The unique identifier (primary key) of the category to delete.
            Must be a positive integer. Provided as a path parameter.
        category_dao: The category DAO instance for database operations.
            Injected via FastAPI dependency injection.

    Returns:
        No content (204 status code) on successful deletion. The response body
        will be empty.

    Raises:
        HTTPException: 404 Not Found if the category with the given ID does not exist.
        HTTPException: 500 Internal Server Error if database operation fails,
            including cases where foreign key constraints prevent deletion.

    Example:
        DELETE /category/42

    Note:
        This is a destructive operation and cannot be undone. Ensure that the
        category has no dependent entities before deletion.

    """
    try:
        await category_dao.delete(category_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail="Category not found") from e
    except DBException as e:
        raise HTTPException(status_code=500, detail="There was an error deleting the category") from e
