"""Authenticated HTTP API routes for expense products.

Provides the paginated product list for any authenticated user.
Access is enforced on the router via ``user_authorized``. Admin-only
mutating and single-item read routes live in ``admin_only``.

Routes:
    GET /product - Paginated product list
"""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

from expenses_counter.modules.middlewares.dependencies import get_db
from expenses_counter.modules.middlewares.dependencies.user_authorized import user_authorized
from expenses_counter.modules.routers.schemas.base.metadata import PaginationMetadata
from expenses_counter.modules.routers.schemas.requests.product import (
    GetAllProductsQuery,
)
from expenses_counter.modules.routers.schemas.responses.product import (
    GetAllProductsResponse,
    SimpleProductGet,
)
from expenses_counter.services.daos import ProductDAO
from expenses_counter.services.database import AsyncDatabaseClient

router = APIRouter(prefix="/product", dependencies=[Depends(user_authorized)])


@router.get("", response_model=GetAllProductsResponse, status_code=status.HTTP_200_OK)
async def get_product_list(
    query: Annotated[GetAllProductsQuery, Query(description="Pagination and sorting parameters")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetAllProductsResponse:
    """Return all products with pagination metadata.

    Args:
        query (GetAllProductsQuery): Pagination and sort parameters.
        db (AsyncDatabaseClient): Database client for the request.

    Returns:
        GetAllProductsResponse: Products and pagination metadata.

    Raises:
        HTTPException: 500 if a database error occurs while listing products.

    """
    product_dao = ProductDAO(database_client=db)

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
