"""HTTP API routes for shops.

Provides list, read, create, update, and delete endpoints for shops linked to
categories. The list endpoint supports pagination and sorting.

Routes:
    GET /shop - Paginated list of all shops
    GET /shop/{shop_id} - Single shop by id
    POST /shop - Create a shop
    PUT /shop/{shop_id} - Replace a shop
    DELETE /shop/{shop_id} - Delete a shop
"""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from loguru import logger
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError

from expenses_counter.modules.middlewares.dependencies.admin_required import admin_required
from expenses_counter.modules.middlewares.dependencies.daos import get_shop
from expenses_counter.modules.routers.schemas.base.metadata import PaginationMetadata
from expenses_counter.modules.routers.schemas.requests.shop import (
    GetAllShopsQuery,
    PatchShopBody,
    PostShopBody,
    PutShopBody,
)
from expenses_counter.modules.routers.schemas.responses.shop import (
    GetAllShopsResponse,
    GetSingleShopResponse,
    SimpleShopGet,
)
from expenses_counter.services.daos import ShopDAO

router = APIRouter(prefix="/shop", tags=["Shop"], dependencies=[Depends(admin_required)])


@router.get("", response_model=GetAllShopsResponse, status_code=status.HTTP_200_OK)
async def get_shop_list(
    shop_dao: Annotated[ShopDAO, Depends(get_shop)],
    query: Annotated[GetAllShopsQuery, Query(description="Pagination and sorting parameters")],
) -> GetAllShopsResponse:
    """Return all shops with pagination metadata.

    Args:
        shop_dao (ShopDAO): Shop data access object.
        query (GetAllShopsQuery): Pagination and sort parameters.

    Returns:
        GetAllShopsResponse: Shops and pagination metadata.

    Raises:
        HTTPException: 500 if a database error occurs while listing shops.

    """
    try:
        data, total = await shop_dao.get_all(**query.model_dump())
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while retrieving the shop list", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while retrieving the shop list",
        ) from e

    metadata = PaginationMetadata(total=total, **query.model_dump())
    return GetAllShopsResponse(data=[SimpleShopGet.model_validate(shop) for shop in data], metadata=metadata)


@router.get("/{shop_id}", response_model=GetSingleShopResponse)
async def get_shop_by_id(
    shop_id: Annotated[int, Path(description="The unique identifier of the shop to retrieve")],
    shop_dao: Annotated[ShopDAO, Depends(get_shop)],
):
    """Return a single shop by primary key.

    Args:
        shop_id (int): Shop primary key.
        shop_dao (ShopDAO): Shop data access object.

    Returns:
        GetSingleShopResponse: The requested shop payload.

    Raises:
        HTTPException: 404 if no shop exists for ``shop_id``.
        HTTPException: 500 if a database error occurs while loading the shop.

    """
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


@router.post("", response_model=GetSingleShopResponse, status_code=status.HTTP_201_CREATED)
async def create_shop(
    body: Annotated[PostShopBody, Body(description="The shop data to create")],
    shop_dao: Annotated[ShopDAO, Depends(get_shop)],
) -> GetSingleShopResponse:
    """Create a new shop.

    Args:
        body (PostShopBody): Fields for the new shop (e.g. category link).
        shop_dao (ShopDAO): Shop data access object.

    Returns:
        GetSingleShopResponse: The created shop payload.

    Raises:
        HTTPException: 400 if a referenced entity violates integrity (e.g. missing category).
        HTTPException: 500 if a database error occurs while creating the shop.

    """
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


@router.put("/{shop_id}", response_model=GetSingleShopResponse, status_code=status.HTTP_200_OK)
async def update_shop(
    shop_id: Annotated[int, Path(description="The unique identifier of the shop to update")],
    body: Annotated[PutShopBody, Body(description="The shop data to update")],
    shop_dao: Annotated[ShopDAO, Depends(get_shop)],
) -> GetSingleShopResponse:
    """Replace an existing shop by primary key.

    Args:
        shop_id (int): Shop primary key.
        body (PutShopBody): Full replacement payload for the shop.
        shop_dao (ShopDAO): Shop data access object.

    Returns:
        GetSingleShopResponse: The updated shop payload.

    Raises:
        HTTPException: 400 if a referenced entity violates integrity (e.g. invalid category).
        HTTPException: 404 if no shop exists for ``shop_id``.
        HTTPException: 500 if a database error occurs while updating the shop.

    """
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


@router.patch("/{shop_id}", response_model=GetSingleShopResponse, status_code=status.HTTP_200_OK)
async def patch_shop(
    shop_id: Annotated[int, Path(description="The unique identifier of the shop to update")],
    body: Annotated[PatchShopBody, Body(description="The shop data to update")],
    shop_dao: Annotated[ShopDAO, Depends(get_shop)],
) -> GetSingleShopResponse:
    """Patch an existing shop by primary key.

    Args:
        shop_id (int): Shop primary key.
        body (PatchShopBody): Partial update payload for the shop.
        shop_dao (ShopDAO): Shop data access object.

    Returns:
        GetSingleShopResponse: The updated shop payload.

    Raises:
        HTTPException: 400 if a referenced entity violates integrity (e.g. invalid category).
        HTTPException: 404 if no shop exists for ``shop_id``.
        HTTPException: 500 if a database error occurs while patching the shop.

    """
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
    shop_dao: Annotated[ShopDAO, Depends(get_shop)],
) -> None:
    """Delete a shop by primary key.

    Args:
        shop_id (int): Shop primary key.
        shop_dao (ShopDAO): Shop data access object.

    Returns:
        None

    Raises:
        HTTPException: 404 if no shop exists for ``shop_id``.
        HTTPException: 500 if a database error occurs while deleting the shop.

    """
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
