"""Transaction API router module.

This module provides REST API endpoints for managing transactions in the expenses
counter application. It includes full CRUD (Create, Read, Update, Delete) operations
for transactions with support for product and address relationships.

The router handles:
    - Listing transactions with pagination and sorting
    - Retrieving individual transactions with product and address information
    - Creating new transactions with required product and address relationships
    - Updating existing transactions
    - Deleting transactions

All endpoints include proper error handling for database exceptions and return
appropriate HTTP status codes.

Routes:
    GET /transaction - List all transactions with pagination
    GET /transaction/{transaction_id} - Get a single transaction by ID
    POST /transaction - Create a new transaction
    PUT /transaction/{transaction_id} - Update an existing transaction
    DELETE /transaction/{transaction_id} - Delete a transaction
"""

__all__ = ("router",)

from typing import Annotated

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from sqlalchemy.exc import DatabaseError, IntegrityError, NoResultFound

from expenses_counter.modules.middlewares.dependencies.get_db import get_db
from expenses_counter.modules.routers.schemas.base.metadata import PaginationMetadata
from expenses_counter.modules.routers.schemas.requests.transaction import (
    GetAllTransactionsQuery,
    MonthlyBodyRequest,
    MonthlyQuery,
    PostTransactionBody,
    PutTransactionBody,
)
from expenses_counter.modules.routers.schemas.responses.transaction import (
    GetAllTransactionsResponse,
    GetSingleTransactionResponse,
    SimpleTransactionGet,
)
from expenses_counter.services.daos import TransactionDAO
from expenses_counter.services.database import AsyncDatabaseClient
from expenses_counter.services.database.models.transaction import Transaction

router = APIRouter(prefix="/transaction", tags=["Transaction"])


@router.post("/monthly", response_model=GetAllTransactionsResponse)
async def get_transactions_by_date_range(
    body: Annotated[MonthlyBodyRequest, Body(description="The body of the request")],
    query: Annotated[MonthlyQuery, Query(description="The query parameters")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
):
    """Retrieve all transactions by date range.

    Args:
        body: Request body containing the date to filter transactions by month.
        query: Query parameters including sort_by and sort_order.
        db: The database client instance for creating DAO connections.
            Injected via FastAPI dependency injection from get_db.

    Returns:
        GetAllTransactionsResponse containing a list of transactions and pagination metadata.

    Raises:
        HTTPException: 500 Internal Server Error if database operation fails.

    """
    start_date = body.date.replace(day=1)
    end_date = start_date + relativedelta(months=1)
    try:
        async with TransactionDAO(database_client=db) as transaction_dao:
            data, total = await transaction_dao.get_all(
                filters=[Transaction.date >= start_date, Transaction.date < end_date],
                limit=None,
                offset=None,
                sort_by=query.sort_by,
                sort_order=query.sort_order,
            )
        metadata = PaginationMetadata(
            total=total, offset=None, limit=None, sort_by=query.sort_by, sort_order=query.sort_order
        )
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Something went wrong while retrieving the transaction list") from e

    return GetAllTransactionsResponse(
        data=[SimpleTransactionGet.model_validate(transaction) for transaction in data], metadata=metadata
    )


@router.get("", response_model=GetAllTransactionsResponse)
async def get_transaction_list(
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
    query: Annotated[GetAllTransactionsQuery, Query(description="Pagination and sorting parameters")],
):
    """Retrieve all transactions with pagination and sorting.

    Args:
        db: The database client instance for creating DAO connections.
            Injected via FastAPI dependency injection from get_db.
        query: Pagination and sorting parameters including limit, offset, sort_by, and sort_order.

    Returns:
        GetAllTransactionsResponse containing a list of transactions and pagination metadata.

    Raises:
        HTTPException: 500 Internal Server Error if database operation fails.

    """
    try:
        async with TransactionDAO(database_client=db) as transaction_dao:
            data, total = await transaction_dao.get_all(
                limit=query.limit, offset=query.offset, sort_by=query.sort_by, sort_order=query.sort_order
            )
        metadata = PaginationMetadata(
            total=total, offset=query.offset, limit=query.limit, sort_by=query.sort_by, sort_order=query.sort_order
        )
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Something went wrong while retrieving the transaction list") from e

    return GetAllTransactionsResponse(
        data=[SimpleTransactionGet.model_validate(transaction) for transaction in data], metadata=metadata
    )


@router.get("/{transaction_id}", response_model=GetSingleTransactionResponse)
async def get_transaction_by_id(
    transaction_id: Annotated[int, Path(description="The unique identifier of the transaction to retrieve")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
):
    """Retrieve a transaction by its ID.

    Args:
        transaction_id: The unique identifier of the transaction to retrieve.
        db: The database client instance for creating DAO connections.
            Injected via FastAPI dependency injection from get_db.

    Returns:
        GetSingleTransactionResponse containing the transaction details.

    Raises:
        HTTPException: 404 Not Found if the transaction is not found.
            500 Internal Server Error if database operation fails.

    """
    try:
        async with TransactionDAO(database_client=db) as transaction_dao:
            transaction = await transaction_dao.get_by_id(transaction_id)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Something went wrong while retrieving the transaction") from e

    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return transaction


@router.post("", response_model=GetSingleTransactionResponse)
async def create_transaction(
    body: PostTransactionBody,
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
):
    """Create a new transaction.

    Args:
        body: The transaction data to create including date, count, price, product_id, and address_id.
        db: The database client instance for creating DAO connections.
            Injected via FastAPI dependency injection from get_db.

    Returns:
        GetSingleTransactionResponse containing the newly created transaction.

    Raises:
        HTTPException: 400 Bad Request if the referenced product or address is not found (IntegrityError).
            500 Internal Server Error if database operation fails.

    """
    try:
        async with TransactionDAO(database_client=db) as transaction_dao:
            return await transaction_dao.create(**body.model_dump(by_alias=False))
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="Product or Address not found") from e
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Something went wrong while creating the transaction") from e


@router.put("/{transaction_id}", response_model=GetSingleTransactionResponse)
async def update_transaction(
    transaction_id: Annotated[int, Path(description="The unique identifier of the transaction to update")],
    body: PutTransactionBody,
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
):
    """Update an existing transaction by replacing all its fields.

    Args:
        transaction_id: The unique identifier of the transaction to update.
        body: The complete transaction data to replace the existing transaction.
        db: The database client instance for creating DAO connections.
            Injected via FastAPI dependency injection from get_db.

    Returns:
        GetSingleTransactionResponse containing the updated transaction.

    Raises:
        HTTPException: 400 Bad Request if the referenced product or address is not found (IntegrityError).
            404 Not Found if the transaction is not found (NoResultFound).
            500 Internal Server Error if database operation fails.

    """
    try:
        async with TransactionDAO(database_client=db) as transaction_dao:
            return await transaction_dao.update(transaction_id, **body.model_dump(by_alias=False))
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="Product or Address not found") from e
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail="Transaction not found") from e
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Something went wrong while updating the transaction") from e


@router.delete("/{transaction_id}", status_code=204)
async def delete_transaction(
    transaction_id: Annotated[int, Path(description="The unique identifier of the transaction to delete")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
):
    """Delete a transaction by its ID.

    Args:
        transaction_id: The unique identifier of the transaction to delete.
        db: The database client instance for creating DAO connections.
            Injected via FastAPI dependency injection from get_db.

    Returns:
        None (204 No Content status code).

    Raises:
        HTTPException: 404 Not Found if the transaction is not found (NoResultFound).
            500 Internal Server Error if database operation fails.

    """
    try:
        async with TransactionDAO(database_client=db) as transaction_dao:
            deleted = await transaction_dao.delete(transaction_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Transaction not found")
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail="Transaction not found") from e
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Something went wrong while deleting the transaction") from e
