"""HTTP API routes for expense transactions.

Provides list, read, create, update, and delete endpoints for user
transactions. List and mutating endpoints scope results to the authenticated
user; admins may read, update, or delete any transaction.

Routes:
    GET /transaction - Paginated list of the current user's transactions
    GET /transaction/{transaction_id} - Single transaction by id
    POST /transaction - Create a transaction for the current user
    PUT /transaction/{transaction_id} - Replace a transaction
    DELETE /transaction/{transaction_id} - Delete a transaction
"""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from loguru import logger
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError

from expenses_counter.modules.middlewares.dependencies import get_db, user_authorized
from expenses_counter.modules.routers.schemas.base.metadata import PaginationMetadata
from expenses_counter.modules.routers.schemas.requests.transaction import (
    GetAllTransactionsQuery,
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
from expenses_counter.services.database.models.user import User

router = APIRouter(prefix="/transaction", tags=["Transaction"])


@router.get("", response_model=GetAllTransactionsResponse, status_code=status.HTTP_200_OK)
async def get_transaction_list(
    query: Annotated[GetAllTransactionsQuery, Query(description="Pagination and sorting parameters")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
    user: Annotated[User, Depends(user_authorized)],
) -> GetAllTransactionsResponse:
    """Return the authenticated user's transactions with pagination metadata.

    Args:
        query (GetAllTransactionsQuery): Pagination and sort parameters.
        db (AsyncDatabaseClient): Database client for the request.
        user (User): Authenticated user whose transactions are listed.

    Returns:
        GetAllTransactionsResponse: Transactions and pagination metadata.

    Raises:
        HTTPException: 500 if a database error occurs while listing transactions.

    """
    transaction_dao = TransactionDAO(database_client=db)
    filters = transaction_dao.concat_filters(query.filters_dict, [Transaction.user_id == user.id])

    try:
        data, total = await transaction_dao.get_all(**query.model_dump(exclude={"filters"}), filters=filters)
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
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
    user: Annotated[User, Depends(user_authorized)],
) -> GetSingleTransactionResponse:
    """Return a single transaction by primary key.

    Non-admin users may only retrieve their own transactions.

    Args:
        transaction_id (int): Transaction primary key.
        db (AsyncDatabaseClient): Database client for the request.
        user (User): Authenticated user requesting the transaction.

    Returns:
        GetSingleTransactionResponse: The requested transaction payload.

    Raises:
        HTTPException: 404 if no matching transaction exists for the user.
        HTTPException: 500 if a database error occurs while loading the transaction.

    """
    transaction_dao = TransactionDAO(database_client=db)
    filters = None if user.is_admin else [Transaction.user_id == user.id]

    try:
        payload = await transaction_dao.get_by_pk(transaction_id, filters=filters)
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
    """Create a new transaction for the authenticated user.

    Args:
        body (PostTransactionBody): Fields for the new transaction.
        db (AsyncDatabaseClient): Database client for the request.
        user (User): Authenticated user who owns the new transaction.

    Returns:
        GetSingleTransactionResponse: The created transaction.

    Raises:
        HTTPException: 400 if a referenced product or address violates integrity.
        HTTPException: 500 if a database error occurs while creating the transaction.

    """
    transaction_dao = TransactionDAO(database_client=db)

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
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
    user: Annotated[User, Depends(user_authorized)],
) -> GetSingleTransactionResponse:
    """Replace an existing transaction with the request body.

    Non-admin users may only update their own transactions.

    Args:
        transaction_id (int): Transaction primary key to update.
        body (PutTransactionBody): Full replacement payload.
        db (AsyncDatabaseClient): Database client for the request.
        user (User): Authenticated user performing the update.

    Returns:
        GetSingleTransactionResponse: The updated transaction.

    Raises:
        HTTPException: 400 if a referenced product or address violates integrity.
        HTTPException: 404 if no matching transaction exists for the user.
        HTTPException: 500 if a database error occurs while updating the transaction.

    """
    transaction_dao = TransactionDAO(database_client=db)
    filters = None if user.is_admin else [Transaction.user_id == user.id]

    try:
        payload = await transaction_dao.update(transaction_id, **body.model_dump(), filters=filters)
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
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
    user: Annotated[User, Depends(user_authorized)],
) -> None:
    """Delete a transaction by primary key.

    Non-admin users may only delete their own transactions.

    Args:
        transaction_id (int): Transaction primary key to delete.
        db (AsyncDatabaseClient): Database client for the request.
        user (User): Authenticated user performing the deletion.

    Returns:
        None

    Raises:
        HTTPException: 404 if no matching transaction exists for the user.
        HTTPException: 500 if a database error occurs while deleting the transaction.

    """
    transaction_dao = TransactionDAO(database_client=db)
    filters = None if user.is_admin else [Transaction.user_id == user.id]

    try:
        await transaction_dao.delete(transaction_id, filters=filters)
    except NoResultFound as e:
        logger.warning("Transaction not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while deleting the transaction", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while deleting the transaction",
        ) from e
