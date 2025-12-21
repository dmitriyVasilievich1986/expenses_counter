"""Product router module."""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from expenses_counter.services.daos import ProductDAO
from expenses_counter.services.daos.product.schemas import (
    ProductGet,
    ProductPatch,
    ProductPost,
    ProductPut,
)
from expenses_counter.modules.middlewares.dependencies import get_product

router = APIRouter(prefix="/product", tags=["Product"])


@router.get("", response_model=list[ProductGet])
async def get_product_list(
    product_dao: Annotated[ProductDAO, Depends(get_product)],
):
    """Retrieve all products.

    Args:
        product_dao: The product DAO instance.

    Returns:
        A list of all products in the system.

    """
    return await product_dao.get_all()


@router.get("/{product_id}", response_model=ProductGet)
async def get_product_by_id(
    product_id: int,
    product_dao: Annotated[ProductDAO, Depends(get_product)],
):
    """Retrieve a product by its ID.

    Args:
        product_id: The unique identifier of the product to retrieve.
        product_dao: The product DAO instance.

    """
    product = await product_dao.get_by_id(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("", response_model=ProductGet)
async def create_product(
    product: ProductPost,
    product_dao: Annotated[ProductDAO, Depends(get_product)],
):
    """Create a new product.

    Args:
        product: The product data to create.
        product_dao: The product DAO instance.

    Raises:
        HTTPException: If the product data is invalid or creation fails,
            returns a 400 Bad Request error with details.

    Returns:
        The newly created product.

    """
    try:
        return await product_dao.create(product)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.put("/{product_id}", response_model=ProductGet)
async def update_product(
    product_id: int,
    product: ProductPut,
    product_dao: Annotated[ProductDAO, Depends(get_product)],
):
    """Update an existing product by replacing all its fields.

    Args:
        product_id: The unique identifier of the product to update.
        product: The complete product data to replace the existing product.
        product_dao: The product DAO instance.

    Raises:
        HTTPException: If the product data is invalid or update fails,
            returns a 400 Bad Request error with details.

    Returns:
        The updated product.

    """
    try:
        return await product_dao.update(product_id, product)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.patch("/{product_id}", response_model=ProductGet)
async def patch_product(
    product_id: int,
    product: ProductPatch,
    product_dao: Annotated[ProductDAO, Depends(get_product)],
):
    """Update an existing product by replacing only the provided fields.

    Args:
        product_id: The unique identifier of the product to update.
        product: The partial product data to update. Only provided fields
            will be updated.
        product_dao: The product DAO instance.

    """
    try:
        return await product_dao.modify(product_id, product)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    product_dao: Annotated[ProductDAO, Depends(get_product)],
):
    """Delete a product by its ID.

    Args:
        product_id: The unique identifier of the product to delete.
        product_dao: The product DAO instance.

    Returns:
        None.

    """
    try:
        return await product_dao.delete(product_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
