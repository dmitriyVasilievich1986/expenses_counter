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
    PATCH /product/{product_id} - Partial update of a product
    DELETE /product/{product_id} - Delete a product
"""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from loguru import logger
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError

from expenses_counter.modules.middlewares.dependencies.daos import get_product
from expenses_counter.modules.routers.schemas.base.metadata import PaginationMetadata
from expenses_counter.modules.routers.schemas.requests.product import (
    GetAllProductsQuery,
    PatchProductBody,
    PostProductBody,
    PutProductBody,
)
from expenses_counter.modules.routers.schemas.responses.product import (
    GetAllProductsResponse,
    GetSingleProductResponse,
    SimpleProductGet,
)
from expenses_counter.services.daos import ProductDAO

router = APIRouter(prefix="/product", tags=["Product"])


@router.get("", response_model=GetAllProductsResponse, status_code=status.HTTP_200_OK)
async def get_product_list(
    product_dao: Annotated[ProductDAO, Depends(get_product)],
    query: Annotated[GetAllProductsQuery, Query(description="Pagination and sorting parameters")],
) -> GetAllProductsResponse:
    """Return all products with pagination metadata.

    Args:
        product_dao (ProductDAO): Product data access object.
        query (GetAllProductsQuery): Pagination and sort parameters.

    Returns:
        GetAllProductsResponse: Products and pagination metadata.

    Raises:
        HTTPException: 500 if a database error occurs while listing products.

    """
    try:
        data, total = await product_dao.get_all(**query.model_dump())
        metadata = PaginationMetadata(total=total, **query.model_dump())
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while retrieving the product list", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while retrieving the product list",
        ) from e

    return GetAllProductsResponse(
        data=[SimpleProductGet.model_validate(product) for product in data], metadata=metadata
    )


@router.get("/{product_id}", response_model=GetSingleProductResponse, status_code=status.HTTP_200_OK)
async def get_product_by_id(
    product_id: Annotated[int, Path(description="The unique identifier of the product to retrieve")],
    product_dao: Annotated[ProductDAO, Depends(get_product)],
) -> GetSingleProductResponse:
    """Return a single product by primary key.

    Args:
        product_id (int): Product primary key.
        product_dao (ProductDAO): Product data access object.

    Returns:
        GetSingleProductResponse: The requested product payload.

    Raises:
        HTTPException: 404 if no product exists for ``product_id``.
        HTTPException: 500 if a database error occurs while loading the product.

    """
    try:
        return await product_dao.get_by_pk(product_id)
    except NoResultFound as e:
        logger.warning("Product not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while retrieving the product", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while retrieving the product",
        ) from e


@router.post("", response_model=GetSingleProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    body: Annotated[PostProductBody, Body(description="The product data to create")],
    product_dao: Annotated[ProductDAO, Depends(get_product)],
) -> GetSingleProductResponse:
    """Create a new product.

    Args:
        body (PostProductBody): Fields for the new product (e.g. category link).
        product_dao (ProductDAO): Product data access object.

    Returns:
        GetSingleProductResponse: The created product payload.

    Raises:
        HTTPException: 400 if a referenced entity violates integrity (e.g. missing category).
        HTTPException: 500 if a database error occurs while creating the product.

    """
    try:
        return await product_dao.create(**body.model_dump())
    except IntegrityError as e:
        logger.exception("Related object not found", exc_info=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related object not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while creating the product", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while creating the product",
        ) from e


@router.put("/{product_id}", response_model=GetSingleProductResponse, status_code=status.HTTP_200_OK)
async def update_product(
    product_id: Annotated[int, Path(description="The unique identifier of the product to update")],
    body: Annotated[PutProductBody, Body(description="The product data to update")],
    product_dao: Annotated[ProductDAO, Depends(get_product)],
) -> GetSingleProductResponse:
    """Replace an existing product by primary key.

    Args:
        product_id (int): Product primary key.
        body (PutProductBody): Full replacement payload for the product.
        product_dao (ProductDAO): Product data access object.

    Returns:
        GetSingleProductResponse: The updated product payload.

    Raises:
        HTTPException: 400 if a referenced entity violates integrity (e.g. invalid category).
        HTTPException: 404 if no product exists for ``product_id``.
        HTTPException: 500 if a database error occurs while updating the product.

    """
    try:
        return await product_dao.update(product_id, **body.model_dump())
    except IntegrityError as e:
        logger.exception("Related object not found", exc_info=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related object not found") from e
    except NoResultFound as e:
        logger.warning("Product not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while updating the product", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while updating the product",
        ) from e


@router.patch("/{product_id}", response_model=GetSingleProductResponse, status_code=status.HTTP_200_OK)
async def patch_product(
    product_id: Annotated[int, Path(description="The unique identifier of the product to update")],
    body: Annotated[PatchProductBody, Body(description="The product data to update")],
    product_dao: Annotated[ProductDAO, Depends(get_product)],
) -> GetSingleProductResponse:
    """Patch an existing product by primary key.

    Args:
        product_id (int): Product primary key.
        body (PatchProductBody): Partial update payload for the product.
        product_dao (ProductDAO): Product data access object.

    Returns:
        GetSingleProductResponse: The updated product payload.

    Raises:
        HTTPException: 400 if a referenced entity violates integrity (e.g. invalid category).
        HTTPException: 404 if no product exists for ``product_id``.
        HTTPException: 500 if a database error occurs while patching the product.

    """
    try:
        return await product_dao.update(product_id, **body.model_dump(exclude_unset=True))
    except IntegrityError as e:
        logger.exception("Related object not found", exc_info=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related object not found") from e
    except NoResultFound as e:
        logger.warning("Product not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while patching the product", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while patching the product",
        ) from e


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: Annotated[int, Path(description="The unique identifier of the product to delete")],
    product_dao: Annotated[ProductDAO, Depends(get_product)],
) -> None:
    """Delete a product by primary key.

    Args:
        product_id (int): Product primary key.
        product_dao (ProductDAO): Product data access object.

    Returns:
        None

    Raises:
        HTTPException: 404 if no product exists for ``product_id``.
        HTTPException: 500 if a database error occurs while deleting the product.

    """
    try:
        await product_dao.delete(product_id)
    except NoResultFound as e:
        logger.warning("Product not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while deleting the product", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while deleting the product",
        ) from e
