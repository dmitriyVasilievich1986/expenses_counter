"""Authenticated HTTP API routes for expense categories.

Provides the paginated category list for any authenticated user.
Access is enforced on the router via ``user_authorized``. Admin-only
mutating and single-item read routes live in ``admin_only``.

Routes:
    GET /category - Paginated category list
"""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

from expenses_counter.modules.middlewares.dependencies import get_db, user_authorized
from expenses_counter.modules.routers.schemas.base.metadata import PaginationMetadata
from expenses_counter.modules.routers.schemas.requests.category import (
    GetAllCategoriesQuery,
)
from expenses_counter.modules.routers.schemas.responses.category import (
    GetAllCategoriesResponse,
    SimpleCategoryGet,
)
from expenses_counter.services.daos import CategoryDAO
from expenses_counter.services.database import AsyncDatabaseClient

router = APIRouter(prefix="/category", dependencies=[Depends(user_authorized)])


@router.get("", response_model=GetAllCategoriesResponse, status_code=status.HTTP_200_OK)
async def get_category_list(
    query: Annotated[GetAllCategoriesQuery, Query(description="Pagination and sorting parameters")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetAllCategoriesResponse:
    """Return all categories with pagination metadata.

    Args:
        query (GetAllCategoriesQuery): Pagination and sort parameters.
        db (AsyncDatabaseClient): Database client for the request.

    Returns:
        GetAllCategoriesResponse: Categories and pagination metadata.

    Raises:
        HTTPException: 500 if a database error occurs while listing categories.

    """
    category_dao = CategoryDAO(database_client=db)

    try:
        data, total = await category_dao.get_all(**query.model_dump())
        metadata = PaginationMetadata(total=total, **query.model_dump())
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while retrieving the category list", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while retrieving the category list",
        ) from e

    return GetAllCategoriesResponse(
        data=[SimpleCategoryGet.model_validate(category) for category in data], metadata=metadata
    )
