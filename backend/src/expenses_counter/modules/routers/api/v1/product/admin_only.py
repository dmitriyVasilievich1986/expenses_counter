"""Admin-only HTTP API routes for expense products.

Provides read, create, update, and delete endpoints for products.
Admin access is enforced on the router via ``admin_required``. The
paginated list endpoint lives in ``all_users``.

Routes:
    GET /product/{product_id} - Single product by id
    POST /product - Create a product
    PUT /product/{product_id} - Replace a product
    PATCH /product/{product_id} - Partially update a product
    DELETE /product/{product_id} - Delete a product
"""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from loguru import logger
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError

from expenses_counter.modules.middlewares.dependencies import get_db
from expenses_counter.modules.middlewares.dependencies.admin_required import admin_required
from expenses_counter.modules.routers.schemas.requests.product import (
    PatchProductBody,
    PostProductBody,
    PutProductBody,
)
from expenses_counter.modules.routers.schemas.responses.product import (
    GetSingleProductResponse,
)
from expenses_counter.services.daos import ProductDAO
from expenses_counter.services.database import AsyncDatabaseClient

router = APIRouter(prefix="/product", dependencies=[Depends(admin_required)])


@router.get(
    "/{product_id}",
    response_model=GetSingleProductResponse,
    status_code=status.HTTP_200_OK,
)
async def get_product_by_id(
    product_id: Annotated[int, Path(description="The unique identifier of the product to retrieve")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleProductResponse:
    """Return a single product by primary key.

    Args:
        product_id (int): Product primary key.
        db (AsyncDatabaseClient): Database client for the request.

    Returns:
        GetSingleProductResponse: The requested product payload.

    Raises:
        HTTPException: 404 if no product exists for ``product_id``.
        HTTPException: 500 if a database error occurs while loading the product.

    """
    product_dao = ProductDAO(database_client=db)

    try:
        payload = await product_dao.get_by_pk(product_id)
    except NoResultFound as e:
        logger.warning("Product not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while retrieving the product", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while retrieving the product",
        ) from e

    return GetSingleProductResponse.model_validate(payload)


@router.post(
    "",
    response_model=GetSingleProductResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    body: Annotated[PostProductBody, Body(description="The product data to create")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleProductResponse:
    """Create a new product.

    Args:
        body (PostProductBody): Fields for the new product (e.g. sub-category link).
        db (AsyncDatabaseClient): Database client for the request.

    Returns:
        GetSingleProductResponse: The created product payload.

    Raises:
        HTTPException: 400 if a referenced entity violates integrity (e.g. missing category).
        HTTPException: 500 if a database error occurs while creating the product.

    """
    product_dao = ProductDAO(database_client=db)

    try:
        payload = await product_dao.create(**body.model_dump())
    except IntegrityError as e:
        logger.exception("Related object not found", exc_info=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related object not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while creating the product", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while creating the product",
        ) from e

    return GetSingleProductResponse.model_validate(payload)


@router.put(
    "/{product_id}",
    response_model=GetSingleProductResponse,
    status_code=status.HTTP_200_OK,
)
async def update_product(
    product_id: Annotated[int, Path(description="The unique identifier of the product to update")],
    body: Annotated[PutProductBody, Body(description="The product data to update")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleProductResponse:
    """Replace an existing product by primary key.

    Args:
        product_id (int): Product primary key.
        body (PutProductBody): Full replacement payload for the product.
        db (AsyncDatabaseClient): Database client for the request.

    Returns:
        GetSingleProductResponse: The updated product payload.

    Raises:
        HTTPException: 400 if a referenced entity violates integrity (e.g. invalid category).
        HTTPException: 404 if no product exists for ``product_id``.
        HTTPException: 500 if a database error occurs while updating the product.

    """
    product_dao = ProductDAO(database_client=db)

    try:
        payload = await product_dao.update(product_id, **body.model_dump())
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

    return GetSingleProductResponse.model_validate(payload)


@router.patch(
    "/{product_id}",
    response_model=GetSingleProductResponse,
    status_code=status.HTTP_200_OK,
)
async def patch_product(
    product_id: Annotated[int, Path(description="The unique identifier of the product to update")],
    body: Annotated[PatchProductBody, Body(description="The product data to update")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleProductResponse:
    """Patch an existing product by primary key.

    Args:
        product_id (int): Product primary key.
        body (PatchProductBody): Partial update payload for the product.
        db (AsyncDatabaseClient): Database client for the request.

    Returns:
        GetSingleProductResponse: The updated product payload.

    Raises:
        HTTPException: 400 if a referenced entity violates integrity (e.g. invalid category).
        HTTPException: 404 if no product exists for ``product_id``.
        HTTPException: 500 if a database error occurs while patching the product.

    """
    product_dao = ProductDAO(database_client=db)

    try:
        payload = await product_dao.update(product_id, **body.model_dump(exclude_unset=True))
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

    return GetSingleProductResponse.model_validate(payload)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: Annotated[int, Path(description="The unique identifier of the product to delete")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> None:
    """Delete a product by primary key.

    Args:
        product_id (int): Product primary key.
        db (AsyncDatabaseClient): Database client for the request.

    Returns:
        None

    Raises:
        HTTPException: 404 if no product exists for ``product_id``.
        HTTPException: 500 if a database error occurs while deleting the product.

    """
    product_dao = ProductDAO(database_client=db)

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
