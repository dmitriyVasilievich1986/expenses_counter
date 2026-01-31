"""Shop API router module.

This module provides REST API endpoints for managing shops in the expenses
counter application. It includes full CRUD (Create, Read, Update, Delete) operations
for shops with support for category relationships.

The router handles:
    - Listing shops with pagination and sorting
    - Retrieving individual shops with category information
    - Creating new shops with optional category relationships
    - Updating existing shops
    - Deleting shops

All endpoints include proper error handling for database exceptions and return
appropriate HTTP status codes.

Routes:
    GET /shop - List all shops with pagination
    GET /shop/{shop_id} - Get a single shop by ID
    POST /shop - Create a new shop
    PUT /shop/{shop_id} - Update an existing shop
    DELETE /shop/{shop_id} - Delete a shop
"""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.exc import DatabaseError, IntegrityError, NoResultFound

from expenses_counter.modules.middlewares.dependencies.get_db import get_db
from expenses_counter.modules.routers.schemas.base.metadata import PaginationMetadata
from expenses_counter.modules.routers.schemas.requests.shop import (
    GetAllShopsQuery,
    PostShopBody,
    PutShopBody,
)
from expenses_counter.modules.routers.schemas.responses.shop import (
    GetAllShopsResponse,
    GetSingleShopResponse,
    SimpleShopGet,
)
from expenses_counter.services.daos import ShopDAO
from expenses_counter.services.database import AsyncDatabaseClient

router = APIRouter(prefix="/shop", tags=["Shop"])


@router.get("", response_model=GetAllShopsResponse)
async def get_shop_list(
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
    query: Annotated[GetAllShopsQuery, Query(description="Pagination and sorting parameters")],
):
    """Retrieve all shops with pagination and sorting.

    Args:
        db: The database client instance for creating DAO connections.
            Injected via FastAPI dependency injection from get_db.
        query: Pagination and sorting parameters including limit, offset, sort_by, and sort_order.

    Returns:
        GetAllShopsResponse containing a list of shops and pagination metadata.

    Raises:
        HTTPException: 500 Internal Server Error if database operation fails.

    """
    try:
        async with ShopDAO(database_client=db) as shop_dao:
            data, total = await shop_dao.get_all(
                limit=query.limit, offset=query.offset, sort_by=query.sort_by, sort_order=query.sort_order
            )
        metadata = PaginationMetadata(
            total=total, offset=query.offset, limit=query.limit, sort_by=query.sort_by, sort_order=query.sort_order
        )
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Something went wrong while retrieving the shop list") from e

    return GetAllShopsResponse(data=[SimpleShopGet.model_validate(shop) for shop in data], metadata=metadata)


@router.get("/{shop_id}", response_model=GetSingleShopResponse)
async def get_shop_by_id(
    shop_id: Annotated[int, Path(description="The unique identifier of the shop to retrieve")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
):
    """Retrieve a shop by its ID.

    Args:
        shop_id: The unique identifier of the shop to retrieve.
        db: The database client instance for creating DAO connections.
            Injected via FastAPI dependency injection from get_db.

    Returns:
        GetSingleShopResponse containing the shop details.

    Raises:
        HTTPException: 404 Not Found if the shop is not found.
            500 Internal Server Error if database operation fails.

    """
    try:
        async with ShopDAO(database_client=db) as shop_dao:
            shop = await shop_dao.get_by_id(shop_id)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Something went wrong while retrieving the shop") from e

    if shop is None:
        raise HTTPException(status_code=404, detail="Shop not found")

    return shop


@router.post("", response_model=GetSingleShopResponse)
async def create_shop(
    body: PostShopBody,
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
):
    """Create a new shop.

    Args:
        body: The shop data to create including name, icon, description, and optional category_id.
        db: The database client instance for creating DAO connections.
            Injected via FastAPI dependency injection from get_db.

    Returns:
        GetSingleShopResponse containing the newly created shop.

    Raises:
        HTTPException: 400 Bad Request if the referenced category is not found (IntegrityError).
            500 Internal Server Error if database operation fails.

    """
    try:
        async with ShopDAO(database_client=db) as shop_dao:
            return await shop_dao.create(**body.model_dump(by_alias=False))
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="Category not found") from e
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Something went wrong while creating the shop") from e


@router.put("/{shop_id}", response_model=GetSingleShopResponse)
async def update_shop(
    shop_id: Annotated[int, Path(description="The unique identifier of the shop to update")],
    body: PutShopBody,
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
):
    """Update an existing shop by replacing all its fields.

    Args:
        shop_id: The unique identifier of the shop to update.
        body: The complete shop data to replace the existing shop.
        db: The database client instance for creating DAO connections.
            Injected via FastAPI dependency injection from get_db.

    Returns:
        GetSingleShopResponse containing the updated shop.

    Raises:
        HTTPException: 400 Bad Request if the referenced category is not found (IntegrityError).
            404 Not Found if the shop is not found (NoResultFound).
            500 Internal Server Error if database operation fails.

    """
    try:
        async with ShopDAO(database_client=db) as shop_dao:
            return await shop_dao.update(shop_id, **body.model_dump(by_alias=False))
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="Category not found") from e
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail="Shop not found") from e
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Something went wrong while updating the shop") from e


@router.delete("/{shop_id}", status_code=204)
async def delete_shop(
    shop_id: Annotated[int, Path(description="The unique identifier of the shop to delete")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
):
    """Delete a shop by its ID.

    Args:
        shop_id: The unique identifier of the shop to delete.
        db: The database client instance for creating DAO connections.
            Injected via FastAPI dependency injection from get_db.

    Returns:
        None (204 No Content status code).

    Raises:
        HTTPException: 404 Not Found if the shop is not found (NoResultFound).
            500 Internal Server Error if database operation fails.

    """
    try:
        async with ShopDAO(database_client=db) as shop_dao:
            deleted = await shop_dao.delete(shop_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Shop not found")
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail="Shop not found") from e
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Something went wrong while deleting the shop") from e
