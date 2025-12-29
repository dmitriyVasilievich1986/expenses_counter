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

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from expenses_counter.modules.middlewares.dependencies import get_transaction
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
from expenses_counter.services.daos.base.exceptions import DBException, NotFoundException, RelationshipNotFoundException

router = APIRouter(prefix="/transaction", tags=["Transaction"])


@router.get("", response_model=GetAllTransactionsResponse)
async def get_transaction_list(
    transaction_dao: Annotated[TransactionDAO, Depends(get_transaction)],
    query: Annotated[GetAllTransactionsQuery, Query(description="Pagination and sorting parameters")],
):
    """Retrieve all transactions with pagination and sorting.

    Args:
        transaction_dao: The transaction DAO instance.
        query: Pagination and sorting parameters including limit, offset, sort_by, and sort_order.

    Returns:
        GetAllTransactionsResponse containing a list of transactions and pagination metadata.

    Raises:
        HTTPException: If retrieval fails, returns a 500 Internal Server Error.

    """
    try:
        data, total = await transaction_dao.get_all(
            limit=query.limit, offset=query.offset, sort_by=query.sort_by, sort_order=query.sort_order
        )
        metadata = PaginationMetadata(
            total=total, offset=query.offset, limit=query.limit, sort_by=query.sort_by, sort_order=query.sort_order
        )
    except DBException as e:
        raise HTTPException(status_code=500, detail="Something went wrong while retrieving the transaction list") from e

    return GetAllTransactionsResponse(
        data=[SimpleTransactionGet.model_validate(transaction) for transaction in data], metadata=metadata
    )


@router.get("/{transaction_id}", response_model=GetSingleTransactionResponse)
async def get_transaction_by_id(
    transaction_id: Annotated[int, Path(description="The unique identifier of the transaction to retrieve")],
    transaction_dao: Annotated[TransactionDAO, Depends(get_transaction)],
):
    """Retrieve a transaction by its ID.

    Args:
        transaction_id: The unique identifier of the transaction to retrieve.
        transaction_dao: The transaction DAO instance.

    Returns:
        GetSingleTransactionResponse containing the transaction details.

    Raises:
        HTTPException: If the transaction is not found, returns a 404 Not Found error.
            If retrieval fails, returns a 500 Internal Server Error.

    """
    try:
        transaction = await transaction_dao.get_by_id(transaction_id)
    except DBException as e:
        raise HTTPException(status_code=500, detail="Something went wrong while retrieving the transaction") from e

    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return transaction


@router.post("", response_model=GetSingleTransactionResponse)
async def create_transaction(
    body: PostTransactionBody,
    transaction_dao: Annotated[TransactionDAO, Depends(get_transaction)],
):
    """Create a new transaction.

    Args:
        body: The transaction data to create including date, count, price, product_id, and address_id.
        transaction_dao: The transaction DAO instance.

    Returns:
        GetSingleTransactionResponse containing the newly created transaction.

    Raises:
        HTTPException: If the referenced product or address is not found, returns a 400 Bad Request error.
            If creation fails, returns a 500 Internal Server Error.

    """
    try:
        return await transaction_dao.create(**body.model_dump(by_alias=False))
    except RelationshipNotFoundException as e:
        raise HTTPException(status_code=400, detail="Product or Address not found") from e
    except DBException as e:
        raise HTTPException(status_code=500, detail="Something went wrong while creating the transaction") from e


@router.put("/{transaction_id}", response_model=GetSingleTransactionResponse)
async def update_transaction(
    transaction_id: Annotated[int, Path(description="The unique identifier of the transaction to update")],
    body: PutTransactionBody,
    transaction_dao: Annotated[TransactionDAO, Depends(get_transaction)],
):
    """Update an existing transaction by replacing all its fields.

    Args:
        transaction_id: The unique identifier of the transaction to update.
        body: The complete transaction data to replace the existing transaction.
        transaction_dao: The transaction DAO instance.

    Returns:
        GetSingleTransactionResponse containing the updated transaction.

    Raises:
        HTTPException: If the referenced product or address is not found, returns a 400 Bad Request error.
            If the transaction is not found, returns a 404 Not Found error.
            If update fails, returns a 500 Internal Server Error.

    """
    try:
        return await transaction_dao.update(transaction_id, **body.model_dump(by_alias=False))
    except RelationshipNotFoundException as e:
        raise HTTPException(status_code=400, detail="Product or Address not found") from e
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail="Transaction not found") from e
    except DBException as e:
        raise HTTPException(status_code=500, detail="Something went wrong while updating the transaction") from e


@router.delete("/{transaction_id}", status_code=204)
async def delete_transaction(
    transaction_id: Annotated[int, Path(description="The unique identifier of the transaction to delete")],
    transaction_dao: Annotated[TransactionDAO, Depends(get_transaction)],
):
    """Delete a transaction by its ID.

    Args:
        transaction_id: The unique identifier of the transaction to delete.
        transaction_dao: The transaction DAO instance.

    Returns:
        None (204 No Content status code).

    Raises:
        HTTPException: If the transaction is not found, returns a 404 Not Found error.
            If deletion fails, returns a 500 Internal Server Error.

    """
    try:
        deleted = await transaction_dao.delete(transaction_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Transaction not found")
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail="Transaction not found") from e
    except DBException as e:
        raise HTTPException(status_code=500, detail="Something went wrong while deleting the transaction") from e
