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
    POST /transaction/monthly - List transactions in the month of ``body.date``
    GET /transaction - List all transactions with pagination
    GET /transaction/{transaction_id} - Get a single transaction by ID
    POST /transaction - Create a new transaction
    PUT /transaction/{transaction_id} - Update an existing transaction
    DELETE /transaction/{transaction_id} - Delete a transaction
"""

__all__ = ("router",)

from typing import Annotated

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from loguru import logger
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError

from expenses_counter.modules.middlewares.dependencies import get_db, user_authorized
from expenses_counter.modules.middlewares.dependencies.daos import get_transaction
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
from expenses_counter.services.database.models.user import User
from expenses_counter.utils.filter import Filter

router = APIRouter(prefix="/transaction", tags=["Transaction"])


@router.post("/monthly", response_model=GetAllTransactionsResponse, status_code=status.HTTP_200_OK, deprecated=True)
async def get_transactions_by_date_range(
    body: Annotated[MonthlyBodyRequest, Body(description="The body of the request")],
    query: Annotated[MonthlyQuery, Query(description="The query parameters")],
    transaction_dao: Annotated[TransactionDAO, Depends(get_transaction)],
) -> GetAllTransactionsResponse:
    """Return all transactions whose dates fall in the calendar month of ``body.date``.

    The range is ``[first day of month, first day of next month)``.

    Args:
        body (MonthlyBodyRequest): Request body; ``date`` selects the month.
        query (MonthlyQuery): Sort field and order for the result set.
        transaction_dao (TransactionDAO): Transaction data access object.

    Returns:
        GetAllTransactionsResponse: Transactions in the month and pagination metadata.

    Raises:
        HTTPException: 500 if a database error occurs while listing transactions.

    """
    start_date = body.date.replace(day=1)
    end_date = start_date + relativedelta(months=1)
    filters = [
        Filter[str](column="date", operator="ge", value=start_date),
        Filter[str](column="date", operator="lt", value=end_date),
    ]
    try:
        data, total = await transaction_dao.get_all(
            filters=[f.model_dump() for f in filters],
            limit=None,
            offset=None,
            sort_by=query.sort_by,
            sort_order=query.sort_order,
        )
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while retrieving the transaction list", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while retrieving the transaction list",
        ) from e

    metadata = PaginationMetadata(
        total=total, offset=None, limit=None, sort_by=query.sort_by, sort_order=query.sort_order, filters=filters
    )
    return GetAllTransactionsResponse(
        data=[SimpleTransactionGet.model_validate(transaction) for transaction in data], metadata=metadata
    )


@router.get("", response_model=GetAllTransactionsResponse, status_code=status.HTTP_200_OK)
async def get_transaction_list(
    transaction_dao: Annotated[TransactionDAO, Depends(get_transaction)],
    query: Annotated[GetAllTransactionsQuery, Query(description="Pagination and sorting parameters")],
) -> GetAllTransactionsResponse:
    """Return all transactions with pagination metadata.

    Args:
        transaction_dao (TransactionDAO): Transaction data access object.
        query (GetAllTransactionsQuery): Pagination and sort parameters.

    Returns:
        GetAllTransactionsResponse: Transactions and pagination metadata.

    Raises:
        HTTPException: 500 if a database error occurs while listing transactions.

    """
    try:
        data, total = await transaction_dao.get_all(**query.model_dump())
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while retrieving the transaction list", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while retrieving the transaction list",
        ) from e

    metadata = PaginationMetadata(total=total, **query.model_dump())
    return GetAllTransactionsResponse(
        data=[SimpleTransactionGet.model_validate(transaction) for transaction in data], metadata=metadata
    )


@router.get("/{transaction_id}", response_model=GetSingleTransactionResponse, status_code=status.HTTP_200_OK)
async def get_transaction_by_id(
    transaction_id: Annotated[int, Path(description="The unique identifier of the transaction to retrieve")],
    transaction_dao: Annotated[TransactionDAO, Depends(get_transaction)],
) -> GetSingleTransactionResponse:
    """Return a single transaction by primary key.

    Args:
        transaction_id (int): Transaction primary key.
        transaction_dao (TransactionDAO): Transaction data access object.

    Returns:
        GetSingleTransactionResponse: The requested transaction payload.

    Raises:
        HTTPException: 404 if no transaction exists for ``transaction_id``.
        HTTPException: 500 if a database error occurs while loading the transaction.

    """
    try:
        payload = await transaction_dao.get_by_pk(transaction_id)
    except NoResultFound as e:
        logger.warning("Transaction not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while retrieving the transaction", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while retrieving the transaction",
        ) from e

    return GetSingleTransactionResponse.model_validate(payload)


@router.post("", response_model=GetSingleTransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    body: Annotated[PostTransactionBody, Body(description="The transaction data to create")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
    user: Annotated[User, Depends(user_authorized)],
) -> GetSingleTransactionResponse:
    """Create a new transaction.

    Args:
        body (PostTransactionBody): Fields for the new transaction (e.g. product and address).
        db (AsyncDatabaseClient): Database client.
        user (User): User who is authorized to access the transactions.

    Returns:
        GetSingleTransactionResponse: The created transaction payload.

    Raises:
        HTTPException: 400 if a referenced entity violates integrity (e.g. missing product).
        HTTPException: 500 if a database error occurs while creating the transaction.

    """
    transaction_dao = TransactionDAO(database_client=db, user_id=user.id)
    try:
        payload = await transaction_dao.create(**body.model_dump(), user_id=user.id)
    except IntegrityError as e:
        logger.exception("Related object not found", exc_info=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related object not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while creating the transaction", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while creating the transaction",
        ) from e

    return GetSingleTransactionResponse.model_validate(payload)


@router.put("/{transaction_id}", response_model=GetSingleTransactionResponse, status_code=status.HTTP_200_OK)
async def update_transaction(
    transaction_id: Annotated[int, Path(description="The unique identifier of the transaction to update")],
    body: Annotated[PutTransactionBody, Body(description="The transaction data to update")],
    transaction_dao: Annotated[TransactionDAO, Depends(get_transaction)],
) -> GetSingleTransactionResponse:
    """Replace an existing transaction by primary key.

    Args:
        transaction_id (int): Transaction primary key.
        body (PutTransactionBody): Full replacement payload for the transaction.
        transaction_dao (TransactionDAO): Transaction data access object.

    Returns:
        GetSingleTransactionResponse: The updated transaction payload.

    Raises:
        HTTPException: 400 if a referenced entity violates integrity (e.g. invalid product).
        HTTPException: 404 if no transaction exists for ``transaction_id``.
        HTTPException: 500 if a database error occurs while updating the transaction.

    """
    try:
        payload = await transaction_dao.update(transaction_id, **body.model_dump())
    except IntegrityError as e:
        logger.exception("Related object not found", exc_info=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related object not found") from e
    except NoResultFound as e:
        logger.warning("Transaction not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while updating the transaction", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while updating the transaction",
        ) from e

    return GetSingleTransactionResponse.model_validate(payload)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: Annotated[int, Path(description="The unique identifier of the transaction to delete")],
    transaction_dao: Annotated[TransactionDAO, Depends(get_transaction)],
) -> None:
    """Delete a transaction by primary key.

    Args:
        transaction_id (int): Transaction primary key.
        transaction_dao (TransactionDAO): Transaction data access object.

    Returns:
        None

    Raises:
        HTTPException: 404 if no transaction exists for ``transaction_id``.
        HTTPException: 500 if a database error occurs while deleting the transaction.

    """
    try:
        await transaction_dao.delete(transaction_id)
    except NoResultFound as e:
        logger.warning("Transaction not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while deleting the transaction", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while deleting the transaction",
        ) from e
