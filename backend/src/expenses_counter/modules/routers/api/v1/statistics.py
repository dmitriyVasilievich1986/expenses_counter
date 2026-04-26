"""Statistics API endpoints for expense tracking analytics.

This module provides API routes for retrieving statistical data and insights
about expenses, including spending patterns and product popularity.
"""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

from expenses_counter.modules.middlewares.dependencies.daos import get_transaction
from expenses_counter.modules.routers.schemas.requests.statistics import GetPopularProductsQuery
from expenses_counter.modules.routers.schemas.responses.product import SimpleProductGet
from expenses_counter.modules.routers.schemas.responses.statistics import (
    SpendingsGroupedByMonthResponse,
)
from expenses_counter.services.daos import TransactionDAO

router = APIRouter(prefix="/statistics", tags=["Statistics"])


@router.get(
    "/spendings/grouped-by-month", response_model=list[SpendingsGroupedByMonthResponse], status_code=status.HTTP_200_OK
)
async def get_spendings_grouped_by_month(
    transaction_dao: Annotated[TransactionDAO, Depends(get_transaction)],
) -> list[SpendingsGroupedByMonthResponse]:
    """Return total spendings aggregated by calendar month.

    Args:
        transaction_dao (TransactionDAO): Transaction data access object.

    Returns:
        list[SpendingsGroupedByMonthResponse]: One entry per month with summed spendings.

    Raises:
        HTTPException: 500 if a database error occurs while aggregating spendings.

    """
    try:
        data = await transaction_dao.get_spendings_grouped_by_month()
        logger.info(f"Spendings grouped by month: {data}")
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while retrieving the spendings grouped by month", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while retrieving the spendings grouped by month",
        ) from e

    return [SpendingsGroupedByMonthResponse(month=month, spendings=spendings) for month, spendings in data]


@router.get("/most-popular-products", response_model=list[SimpleProductGet], status_code=status.HTTP_200_OK)
async def get_most_popular_products(
    transaction_dao: Annotated[TransactionDAO, Depends(get_transaction)],
    query: Annotated[GetPopularProductsQuery, Query(description="The query parameters")],
) -> list[SimpleProductGet]:
    """Return products ranked by how often they appear in transactions.

    Args:
        transaction_dao (TransactionDAO): Transaction data access object.
        query (GetPopularProductsQuery): Result size; ``limit`` defaults to 10 (max 100).

    Returns:
        list[SimpleProductGet]: Popular products up to ``query.limit``.

    Raises:
        HTTPException: 500 if a database error occurs while ranking products.

    """
    try:
        return await transaction_dao.get_most_popular_products(limit=query.limit)
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while retrieving the most popular products", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while retrieving the most popular products",
        ) from e
