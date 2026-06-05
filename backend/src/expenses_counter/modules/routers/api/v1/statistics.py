"""HTTP API routes for expense statistics and analytics.

Provides endpoints for spending trends and product popularity. All results
are scoped to the authenticated user's transactions.

Routes:
    GET /statistics/spendings/grouped-by-month - Monthly spending totals
    GET /statistics/most-popular-products - Top products by purchase count
"""

__all__ = ("router",)

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from loguru import logger
from opentelemetry import trace
from sqlalchemy.exc import SQLAlchemyError

from expenses_counter.modules.middlewares.dependencies import get_db, user_authorized
from expenses_counter.modules.routers.schemas.requests.statistics import GetPopularProductsQuery, ProductPriceBody
from expenses_counter.modules.routers.schemas.responses.product import SimpleProductGet
from expenses_counter.modules.routers.schemas.responses.statistics import (
    ProductPriceResponse,
    SpendingsGroupedByMonthResponse,
)
from expenses_counter.services.daos import TransactionDAO
from expenses_counter.services.database import AsyncDatabaseClient
from expenses_counter.services.database.models.transaction import Transaction
from expenses_counter.services.database.models.user import User

router = APIRouter(prefix="/statistics", tags=["Statistics"])

tracer = trace.get_tracer("statistics_api")


@router.get(
    "/spendings/grouped-by-month", response_model=list[SpendingsGroupedByMonthResponse], status_code=status.HTTP_200_OK
)
async def get_spendings_grouped_by_month(
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
    user: Annotated[User, Depends(user_authorized)],
) -> list[SpendingsGroupedByMonthResponse]:
    """Return the authenticated user's total spendings grouped by month.

    Args:
        db (AsyncDatabaseClient): Database client for the request.
        user (User): Authenticated user whose transactions are aggregated.

    Returns:
        list[SpendingsGroupedByMonthResponse]: Monthly spending totals, one
            entry per month with recorded transactions.

    Raises:
        HTTPException: 500 if a database error occurs while aggregating spendings.

    """
    transaction_dao = TransactionDAO(database_client=db)
    filters = [Transaction.user_id == user.id]

    try:
        with tracer.start_as_current_span("get_spendings_grouped_by_month") as span:
            span.set_attribute("user_id", user.id)
            data = await transaction_dao.get_spendings_grouped_by_month(filters=filters)
            logger.info(f"Spendings grouped by month: {data}")
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while retrieving the spendings grouped by month", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while retrieving the spendings grouped by month",
        ) from e

    return [
        SpendingsGroupedByMonthResponse(month=datetime.strptime(month, "%Y-%m-01").date(), spendings=spendings)
        for month, spendings in data
    ]


@router.get("/most-popular-products", response_model=list[SimpleProductGet], status_code=status.HTTP_200_OK)
async def get_most_popular_products(
    query: Annotated[GetPopularProductsQuery, Query(description="The query parameters")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
    user: Annotated[User, Depends(user_authorized)],
) -> list[SimpleProductGet]:
    """Return the most frequently purchased products for the authenticated user.

    Args:
        query (GetPopularProductsQuery): Query parameters, including result limit.
        db (AsyncDatabaseClient): Database client for the request.
        user (User): Authenticated user whose transactions are analyzed.

    Returns:
        list[SimpleProductGet]: Products ordered by purchase frequency, up to
            ``query.limit`` items.

    Raises:
        HTTPException: 500 if a database error occurs while loading popular products.

    """
    transaction_dao = TransactionDAO(database_client=db)
    filters = [Transaction.user_id == user.id]

    try:
        with tracer.start_as_current_span("get_most_popular_products") as span:
            span.set_attribute("user_id", user.id)
            payload = await transaction_dao.get_most_popular_products(limit=query.limit, filters=filters)
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while retrieving the most popular products", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while retrieving the most popular products",
        ) from e

    return [SimpleProductGet.model_validate(product) for product in payload]


@router.post("/product-price", response_model=list[ProductPriceResponse], status_code=status.HTTP_200_OK)
async def get_product_price(
    body: Annotated[ProductPriceBody, Body(description="The request body")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
    user: Annotated[User, Depends(user_authorized)],
) -> list[ProductPriceResponse]:
    """Return the price of the products for the authenticated user."""
    transaction_dao = TransactionDAO(database_client=db)
    filters = transaction_dao.parse_filters([Transaction.product_id.in_(body.product_ids)])

    try:
        with tracer.start_as_current_span("get_product_price") as span:
            span.set_attribute("user_id", user.id)
            data, _ = await transaction_dao.get_all(filters=filters, limit=None)
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while retrieving the product price", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while retrieving the product price",
        ) from e

    return [ProductPriceResponse.model_validate(transaction) for transaction in data]
