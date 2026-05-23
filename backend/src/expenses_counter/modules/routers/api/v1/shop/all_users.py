"""Authenticated HTTP API routes for expense shops.

Provides the paginated shop list for any authenticated user.
Access is enforced on the router via ``user_authorized``. Admin-only
mutating and single-item read routes live in ``admin_only``.

Routes:
    GET /shop - Paginated shop list
"""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

from expenses_counter.modules.middlewares.dependencies import get_db
from expenses_counter.modules.middlewares.dependencies.user_authorized import user_authorized
from expenses_counter.modules.routers.schemas.base.metadata import PaginationMetadata
from expenses_counter.modules.routers.schemas.requests.shop import (
    GetAllShopsQuery,
)
from expenses_counter.modules.routers.schemas.responses.shop import (
    GetAllShopsResponse,
    SimpleShopGet,
)
from expenses_counter.services.daos import ShopDAO
from expenses_counter.services.database import AsyncDatabaseClient

router = APIRouter(prefix="/shop", dependencies=[Depends(user_authorized)])


@router.get("", response_model=GetAllShopsResponse, status_code=status.HTTP_200_OK)
async def get_shop_list(
    query: Annotated[GetAllShopsQuery, Query(description="Pagination and sorting parameters")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetAllShopsResponse:
    """Return all shops with pagination metadata.

    Args:
        query (GetAllShopsQuery): Pagination and sort parameters.
        db (AsyncDatabaseClient): Database client for the request.

    Returns:
        GetAllShopsResponse: Shops and pagination metadata.

    Raises:
        HTTPException: 500 if a database error occurs while listing shops.

    """
    shop_dao = ShopDAO(database_client=db)

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
