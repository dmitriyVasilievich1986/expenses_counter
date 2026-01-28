"""Product API router module.

This module provides REST API endpoints for managing products in the expenses
counter application. It includes full CRUD (Create, Read, Update, Delete) operations
for products with support for category relationships.

The router handles:
    - Listing products with pagination and sorting
    - Retrieving individual products with category information
    - Creating new products with required category relationships
    - Updating existing products
    - Deleting products

All endpoints include proper error handling for database exceptions and return
appropriate HTTP status codes.

Routes:
    GET /product - List all products with pagination
    GET /product/{product_id} - Get a single product by ID
    POST /product - Create a new product
    PUT /product/{product_id} - Update an existing product
    DELETE /product/{product_id} - Delete a product
"""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.exc import DatabaseError, IntegrityError, NoResultFound

from expenses_counter.modules.middlewares.dependencies.get_db import get_db
from expenses_counter.modules.routers.schemas.base.metadata import PaginationMetadata
from expenses_counter.modules.routers.schemas.requests.product import (
    GetAllProductsQuery,
    PostProductBody,
    PutProductBody,
)
from expenses_counter.modules.routers.schemas.responses.product import (
    GetAllProductsResponse,
    GetSingleProductResponse,
    SimpleProductGet,
)
from expenses_counter.services.daos import ProductDAO
from expenses_counter.services.database import AsyncDatabaseClient

router = APIRouter(prefix="/product", tags=["Product"])


@router.get("", response_model=GetAllProductsResponse)
async def get_product_list(
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
    query: Annotated[GetAllProductsQuery, Query(description="Pagination and sorting parameters")],
) -> GetAllProductsResponse:
    """Retrieve all products with pagination and sorting.

    Args:
        db: The database client instance for creating DAO connections.
            Injected via FastAPI dependency injection from get_db.
        query: Pagination and sorting parameters including limit, offset, sort_by, and sort_order.

    Returns:
        GetAllProductsResponse containing a list of products and pagination metadata.

    Raises:
        HTTPException: 500 Internal Server Error if database operation fails.

    """
    try:
        async with ProductDAO(database_client=db) as product_dao:
            data, total = await product_dao.get_all(
                limit=query.limit, offset=query.offset, sort_by=query.sort_by, sort_order=query.sort_order
            )
        metadata = PaginationMetadata(
            total=total, offset=query.offset, limit=query.limit, sort_by=query.sort_by, sort_order=query.sort_order
        )
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Something went wrong while retrieving the product list") from e

    return GetAllProductsResponse(
        data=[SimpleProductGet.model_validate(product) for product in data], metadata=metadata
    )


@router.get("/{product_id}", response_model=GetSingleProductResponse)
async def get_product_by_id(
    product_id: Annotated[int, Path(description="The unique identifier of the product to retrieve")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleProductResponse:
    """Retrieve a product by its ID.

    Args:
        product_id: The unique identifier of the product to retrieve.
        db: The database client instance for creating DAO connections.
            Injected via FastAPI dependency injection from get_db.

    Returns:
        GetSingleProductResponse containing the product details.

    Raises:
        HTTPException: 404 Not Found if the product is not found (NoResultFound).
            500 Internal Server Error if database operation fails.

    """
    try:
        async with ProductDAO(database_client=db) as product_dao:
            product = await product_dao.get_by_id(product_id)
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail="Product not found") from e
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Something went wrong while retrieving the product") from e

    return product


@router.post("", response_model=GetSingleProductResponse)
async def create_product(
    body: PostProductBody,
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleProductResponse:
    """Create a new product.

    Args:
        body: The product data to create including name, sub_category_id, and optional fields.
        db: The database client instance for creating DAO connections.
            Injected via FastAPI dependency injection from get_db.

    Returns:
        GetSingleProductResponse containing the newly created product.

    Raises:
        HTTPException: 400 Bad Request if the referenced category is not found (IntegrityError).
            500 Internal Server Error if database operation fails.

    """
    try:
        async with ProductDAO(database_client=db) as product_dao:
            return await product_dao.create(**body.model_dump(by_alias=False))
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="Category not found") from e
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Something went wrong while creating the product") from e


@router.put("/{product_id}", response_model=GetSingleProductResponse)
async def update_product(
    product_id: Annotated[int, Path(description="The unique identifier of the product to update")],
    body: PutProductBody,
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleProductResponse:
    """Update an existing product by replacing all its fields.

    Args:
        product_id: The unique identifier of the product to update.
        body: The complete product data to replace the existing product.
        db: The database client instance for creating DAO connections.
            Injected via FastAPI dependency injection from get_db.

    Returns:
        GetSingleProductResponse containing the updated product.

    Raises:
        HTTPException: 400 Bad Request if the referenced category is not found (IntegrityError).
            404 Not Found if the product is not found (NoResultFound).
            500 Internal Server Error if database operation fails.

    """
    try:
        async with ProductDAO(database_client=db) as product_dao:
            return await product_dao.update(product_id, **body.model_dump(by_alias=False))
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="Category not found") from e
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail="Product not found") from e
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Something went wrong while updating the product") from e


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: Annotated[int, Path(description="The unique identifier of the product to delete")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> None:
    """Delete a product by its ID.

    Args:
        product_id: The unique identifier of the product to delete.
        db: The database client instance for creating DAO connections.
            Injected via FastAPI dependency injection from get_db.

    Returns:
        None (204 No Content status code).

    Raises:
        HTTPException: 404 Not Found if the product is not found (NoResultFound).
            500 Internal Server Error if database operation fails.

    """
    try:
        async with ProductDAO(database_client=db) as product_dao:
            await product_dao.delete(product_id)
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail="Product not found") from e
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Something went wrong while deleting the product") from e
