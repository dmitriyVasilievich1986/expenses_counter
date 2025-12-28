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

from expenses_counter.modules.middlewares.dependencies import get_product
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
from expenses_counter.services.daos.base.exceptions import DBException, NotFoundException, RelationshipNotFoundException

router = APIRouter(prefix="/product", tags=["Product"])


@router.get("", response_model=GetAllProductsResponse)
async def get_product_list(
    product_dao: Annotated[ProductDAO, Depends(get_product)],
    query: Annotated[GetAllProductsQuery, Query(description="Pagination and sorting parameters")],
):
    """Retrieve all products with pagination and sorting.

    Args:
        product_dao: The product DAO instance.
        query: Pagination and sorting parameters including limit, offset, sort_by, and sort_order.

    Returns:
        GetAllProductsResponse containing a list of products and pagination metadata.

    Raises:
        HTTPException: If retrieval fails, returns a 500 Internal Server Error.

    """
    try:
        data, total = await product_dao.get_all(
            limit=query.limit, offset=query.offset, sort_by=query.sort_by, sort_order=query.sort_order
        )
        metadata = PaginationMetadata(
            total=total, offset=query.offset, limit=query.limit, sort_by=query.sort_by, sort_order=query.sort_order
        )
    except DBException as e:
        raise HTTPException(status_code=500, detail="Something went wrong while retrieving the product list") from e

    return GetAllProductsResponse(
        data=[SimpleProductGet.model_validate(product) for product in data], metadata=metadata
    )


@router.get("/{product_id}", response_model=GetSingleProductResponse)
async def get_product_by_id(
    product_id: Annotated[int, Path(description="The unique identifier of the product to retrieve")],
    product_dao: Annotated[ProductDAO, Depends(get_product)],
):
    """Retrieve a product by its ID.

    Args:
        product_id: The unique identifier of the product to retrieve.
        product_dao: The product DAO instance.

    Returns:
        GetSingleProductResponse containing the product details.

    Raises:
        HTTPException: If the product is not found, returns a 404 Not Found error.
            If retrieval fails, returns a 500 Internal Server Error.

    """
    try:
        product = await product_dao.get_by_id(product_id)
    except DBException as e:
        raise HTTPException(status_code=500, detail="Something went wrong while retrieving the product") from e

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@router.post("", response_model=GetSingleProductResponse)
async def create_product(
    body: PostProductBody,
    product_dao: Annotated[ProductDAO, Depends(get_product)],
):
    """Create a new product.

    Args:
        body: The product data to create including name, category, and optional image path.
        product_dao: The product DAO instance.

    Returns:
        GetSingleProductResponse containing the newly created product.

    Raises:
        HTTPException: If the referenced category is not found, returns a 400 Bad Request error.
            If creation fails, returns a 500 Internal Server Error.

    """
    try:
        return await product_dao.create(**body.model_dump(by_alias=False))
    except RelationshipNotFoundException as e:
        raise HTTPException(status_code=400, detail="Category not found") from e
    except DBException as e:
        raise HTTPException(status_code=500, detail="Something went wrong while creating the product") from e


@router.put("/{product_id}", response_model=GetSingleProductResponse)
async def update_product(
    product_id: Annotated[int, Path(description="The unique identifier of the product to update")],
    body: PutProductBody,
    product_dao: Annotated[ProductDAO, Depends(get_product)],
):
    """Update an existing product by replacing all its fields.

    Args:
        product_id: The unique identifier of the product to update.
        body: The complete product data to replace the existing product.
        product_dao: The product DAO instance.

    Returns:
        GetSingleProductResponse containing the updated product.

    Raises:
        HTTPException: If the referenced category is not found, returns a 400 Bad Request error.
            If the product is not found, returns a 404 Not Found error.
            If update fails, returns a 500 Internal Server Error.

    """
    try:
        return await product_dao.update(product_id, **body.model_dump(by_alias=False))
    except RelationshipNotFoundException as e:
        raise HTTPException(status_code=400, detail="Category not found") from e
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail="Product not found") from e
    except DBException as e:
        raise HTTPException(status_code=500, detail="Something went wrong while updating the product") from e


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: Annotated[int, Path(description="The unique identifier of the product to delete")],
    product_dao: Annotated[ProductDAO, Depends(get_product)],
):
    """Delete a product by its ID.

    Args:
        product_id: The unique identifier of the product to delete.
        product_dao: The product DAO instance.

    Returns:
        None (204 No Content status code).

    Raises:
        HTTPException: If the product is not found, returns a 404 Not Found error.
            If deletion fails, returns a 500 Internal Server Error.

    """
    try:
        await product_dao.delete(product_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail="Product not found") from e
    except DBException as e:
        raise HTTPException(status_code=500, detail="Something went wrong while deleting the product") from e
