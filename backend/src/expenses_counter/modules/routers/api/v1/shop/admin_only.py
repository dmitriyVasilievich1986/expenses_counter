"""Admin-only HTTP API routes for expense shops.

Provides read, create, update, and delete endpoints for shops.
Admin access is enforced on the router via ``admin_required``. The
paginated list endpoint lives in ``all_users``.

Routes:
    GET /shop/{shop_id} - Single shop by id
    POST /shop - Create a shop
    PUT /shop/{shop_id} - Replace a shop
    PATCH /shop/{shop_id} - Partially update a shop
    DELETE /shop/{shop_id} - Delete a shop
"""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from loguru import logger
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError

from expenses_counter.modules.middlewares.dependencies import get_db
from expenses_counter.modules.middlewares.dependencies.admin_required import admin_required
from expenses_counter.modules.routers.schemas.requests.shop import (
    PatchShopBody,
    PostShopBody,
    PutShopBody,
)
from expenses_counter.modules.routers.schemas.responses.shop import (
    GetSingleShopResponse,
)
from expenses_counter.services.daos import ShopDAO
from expenses_counter.services.database import AsyncDatabaseClient

router = APIRouter(prefix="/shop", dependencies=[Depends(admin_required)])


@router.get("/{shop_id}", response_model=GetSingleShopResponse)
async def get_shop_by_id(
    shop_id: Annotated[int, Path(description="The unique identifier of the shop to retrieve")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleShopResponse:
    """Return a single shop by primary key.

    Args:
        shop_id (int): Shop primary key.
        db (AsyncDatabaseClient): Database client for the request.

    Returns:
        GetSingleShopResponse: The requested shop payload.

    Raises:
        HTTPException: 404 if no shop exists for ``shop_id``.
        HTTPException: 500 if a database error occurs while loading the shop.

    """
    shop_dao = ShopDAO(database_client=db)

    try:
        payload = await shop_dao.get_by_pk(shop_id)
    except NoResultFound as e:
        logger.warning("Shop not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shop not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while retrieving the shop", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while retrieving the shop",
        ) from e

    return GetSingleShopResponse.model_validate(payload)


@router.post(
    "",
    response_model=GetSingleShopResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_shop(
    body: Annotated[PostShopBody, Body(description="The shop data to create")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleShopResponse:
    """Create a new shop.

    Args:
        body (PostShopBody): Fields for the new shop (e.g. category link).
        db (AsyncDatabaseClient): Database client for the request.

    Returns:
        GetSingleShopResponse: The created shop payload.

    Raises:
        HTTPException: 400 if a referenced entity violates integrity (e.g. missing category).
        HTTPException: 500 if a database error occurs while creating the shop.

    """
    shop_dao = ShopDAO(database_client=db)

    try:
        payload = await shop_dao.create(**body.model_dump())
    except IntegrityError as e:
        logger.exception("Related object not found", exc_info=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related object not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while creating the shop", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while creating the shop",
        ) from e

    return GetSingleShopResponse.model_validate(payload)


@router.put(
    "/{shop_id}",
    response_model=GetSingleShopResponse,
    status_code=status.HTTP_200_OK,
)
async def update_shop(
    shop_id: Annotated[int, Path(description="The unique identifier of the shop to update")],
    body: Annotated[PutShopBody, Body(description="The shop data to update")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleShopResponse:
    """Replace an existing shop by primary key.

    Args:
        shop_id (int): Shop primary key.
        body (PutShopBody): Full replacement payload for the shop.
        db (AsyncDatabaseClient): Database client for the request.

    Returns:
        GetSingleShopResponse: The updated shop payload.

    Raises:
        HTTPException: 400 if a referenced entity violates integrity (e.g. invalid category).
        HTTPException: 404 if no shop exists for ``shop_id``.
        HTTPException: 500 if a database error occurs while updating the shop.

    """
    shop_dao = ShopDAO(database_client=db)

    try:
        payload = await shop_dao.update(shop_id, **body.model_dump())
    except IntegrityError as e:
        logger.exception("Related object not found", exc_info=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related object not found") from e
    except NoResultFound as e:
        logger.warning("Shop not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shop not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while updating the shop", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while updating the shop",
        ) from e

    return GetSingleShopResponse.model_validate(payload)


@router.patch(
    "/{shop_id}",
    response_model=GetSingleShopResponse,
    status_code=status.HTTP_200_OK,
)
async def patch_shop(
    shop_id: Annotated[int, Path(description="The unique identifier of the shop to update")],
    body: Annotated[PatchShopBody, Body(description="The shop data to update")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleShopResponse:
    """Patch an existing shop by primary key.

    Args:
        shop_id (int): Shop primary key.
        body (PatchShopBody): Partial update payload for the shop.
        db (AsyncDatabaseClient): Database client for the request.

    Returns:
        GetSingleShopResponse: The updated shop payload.

    Raises:
        HTTPException: 400 if a referenced entity violates integrity (e.g. invalid category).
        HTTPException: 404 if no shop exists for ``shop_id``.
        HTTPException: 500 if a database error occurs while patching the shop.

    """
    shop_dao = ShopDAO(database_client=db)

    try:
        payload = await shop_dao.update(shop_id, **body.model_dump(exclude_unset=True))
    except IntegrityError as e:
        logger.exception("Related object not found", exc_info=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related object not found") from e
    except NoResultFound as e:
        logger.warning("Shop not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shop not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while patching the shop", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while patching the shop",
        ) from e

    return GetSingleShopResponse.model_validate(payload)


@router.delete("/{shop_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shop(
    shop_id: Annotated[int, Path(description="The unique identifier of the shop to delete")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> None:
    """Delete a shop by primary key.

    Args:
        shop_id (int): Shop primary key.
        db (AsyncDatabaseClient): Database client for the request.

    Returns:
        None

    Raises:
        HTTPException: 404 if no shop exists for ``shop_id``.
        HTTPException: 500 if a database error occurs while deleting the shop.

    """
    shop_dao = ShopDAO(database_client=db)

    try:
        await shop_dao.delete(shop_id)
    except NoResultFound as e:
        logger.warning("Shop not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shop not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while deleting the shop", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while deleting the shop",
        ) from e
