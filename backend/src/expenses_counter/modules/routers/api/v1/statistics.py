"""Statistics API endpoints for expense tracking analytics.

This module provides API routes for retrieving statistical data and insights
about expenses, including spending patterns and product popularity.
"""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import DatabaseError

from expenses_counter.modules.middlewares.dependencies.get_db import get_db
from expenses_counter.modules.routers.schemas.requests.statistics import GetPopularProductsQuery
from expenses_counter.modules.routers.schemas.responses.product import SimpleProductGet
from expenses_counter.modules.routers.schemas.responses.statistics import (
    SpendingsGroupedByMonthResponse,
)
from expenses_counter.services.daos import TransactionDAO
from expenses_counter.services.database import AsyncDatabaseClient

router = APIRouter(prefix="/statistics", tags=["Statistics"])


@router.get("/spendings/grouped-by-month", response_model=list[SpendingsGroupedByMonthResponse])
async def get_spendings_grouped_by_month(
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> list[SpendingsGroupedByMonthResponse]:
    """Retrieve spending data grouped by month.

    Returns a list of spending totals aggregated by month, providing
    a time-series view of expense patterns.

    Args:
        db: Database client injected by FastAPI dependency injection.

    Returns:
        List of SpendingsGroupedByMonthResponse objects containing month and total spending.

    Raises:
        HTTPException: 500 error if database operation fails.

    """
    try:
        async with TransactionDAO(database_client=db) as transaction_dao:
            data = await transaction_dao.get_spendings_grouped_by_month()
    except DatabaseError as e:
        raise HTTPException(
            status_code=500, detail="Something went wrong while retrieving the spendings grouped by month"
        ) from e

    return [SpendingsGroupedByMonthResponse(month=month, spendings=spendings) for month, spendings in data]


@router.get("/most-popular-products", response_model=list[SimpleProductGet])
async def get_most_popular_products(
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
    query: Annotated[GetPopularProductsQuery, Query(description="The query parameters")],
) -> list[SimpleProductGet]:
    """Retrieve the most frequently purchased products.

    Returns products ordered by purchase frequency, allowing users to identify
    their most commonly bought items.

    Args:
        db: Database client injected by FastAPI dependency injection.
        query: Query parameters including limit for number of results.

    Returns:
        List of SimpleProductGet objects representing the most popular products.

    Raises:
        HTTPException: 500 error if database operation fails.

    """
    try:
        async with TransactionDAO(database_client=db) as transaction_dao:
            return await transaction_dao.get_most_popular_products(limit=query.limit)
    except DatabaseError as e:
        raise HTTPException(
            status_code=500, detail="Something went wrong while retrieving the most popular products"
        ) from e
