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

from expenses_counter.modules.middlewares.dependencies import get_shop
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

router = APIRouter(prefix="/shop", tags=["Shop"])


@router.get("", response_model=GetAllShopsResponse)
async def get_shop_list(
    shop_dao: Annotated[ShopDAO, Depends(get_shop)],
    query: Annotated[GetAllShopsQuery, Query(description="Pagination and sorting parameters")],
):
    """Retrieve all shops with pagination and sorting.

    Args:
        shop_dao: The shop DAO instance.
        query: Pagination and sorting parameters including limit, offset, sort_by, and sort_order.

    Returns:
        GetAllShopsResponse containing a list of shops and pagination metadata.

    Raises:
        HTTPException: If retrieval fails, returns a 500 Internal Server Error.

    """
    try:
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
    shop_dao: Annotated[ShopDAO, Depends(get_shop)],
):
    """Retrieve a shop by its ID.

    Args:
        shop_id: The unique identifier of the shop to retrieve.
        shop_dao: The shop DAO instance.

    Returns:
        GetSingleShopResponse containing the shop details.

    Raises:
        HTTPException: If the shop is not found, returns a 404 Not Found error.
            If retrieval fails, returns a 500 Internal Server Error.

    """
    try:
        shop = await shop_dao.get_by_id(shop_id)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Something went wrong while retrieving the shop") from e

    if shop is None:
        raise HTTPException(status_code=404, detail="Shop not found")

    return shop


@router.post("", response_model=GetSingleShopResponse)
async def create_shop(
    body: PostShopBody,
    shop_dao: Annotated[ShopDAO, Depends(get_shop)],
):
    """Create a new shop.

    Args:
        body: The shop data to create including name, icon, description, and optional category_id.
        shop_dao: The shop DAO instance.

    Returns:
        GetSingleShopResponse containing the newly created shop.

    Raises:
        HTTPException: If the referenced category is not found, returns a 400 Bad Request error.
            If creation fails, returns a 500 Internal Server Error.

    """
    try:
        return await shop_dao.create(**body.model_dump(by_alias=False))
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="Category not found") from e
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Something went wrong while creating the shop") from e


@router.put("/{shop_id}", response_model=GetSingleShopResponse)
async def update_shop(
    shop_id: Annotated[int, Path(description="The unique identifier of the shop to update")],
    body: PutShopBody,
    shop_dao: Annotated[ShopDAO, Depends(get_shop)],
):
    """Update an existing shop by replacing all its fields.

    Args:
        shop_id: The unique identifier of the shop to update.
        body: The complete shop data to replace the existing shop.
        shop_dao: The shop DAO instance.

    Returns:
        GetSingleShopResponse containing the updated shop.

    Raises:
        HTTPException: If the referenced category is not found, returns a 400 Bad Request error.
            If the shop is not found, returns a 404 Not Found error.
            If update fails, returns a 500 Internal Server Error.

    """
    try:
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
    shop_dao: Annotated[ShopDAO, Depends(get_shop)],
):
    """Delete a shop by its ID.

    Args:
        shop_id: The unique identifier of the shop to delete.
        shop_dao: The shop DAO instance.

    Returns:
        None (204 No Content status code).

    Raises:
        HTTPException: If the shop is not found, returns a 404 Not Found error.
            If deletion fails, returns a 500 Internal Server Error.

    """
    try:
        deleted = await shop_dao.delete(shop_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Shop not found")
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail="Shop not found") from e
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Something went wrong while deleting the shop") from e
