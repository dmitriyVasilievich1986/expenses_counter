"""Transaction router module."""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from expenses_counter.daos import TransactionDAO
from expenses_counter.daos.transaction.schemas import (
    TransactionGet,
    TransactionPatch,
    TransactionPost,
    TransactionPut,
)
from expenses_counter.modules.middlewares.dependencies import get_transaction

router = APIRouter(prefix="/transaction", tags=["Transaction"])


@router.get("", response_model=list[TransactionGet])
async def get_transaction_list(
    transaction_dao: Annotated[TransactionDAO, Depends(get_transaction)],
):
    """Retrieve all transactions.

    Args:
        transaction_dao: The transaction DAO instance.

    Returns:
        A list of all transactions in the system.

    """
    return await transaction_dao.get_all()


@router.get("/{transaction_id}", response_model=TransactionGet)
async def get_transaction_by_id(
    transaction_id: int,
    transaction_dao: Annotated[TransactionDAO, Depends(get_transaction)],
):
    """Retrieve a transaction by its ID.

    Args:
        transaction_id: The unique identifier of the transaction to retrieve.
        transaction_dao: The transaction DAO instance.

    """
    transaction = await transaction_dao.get_by_id(transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.post("", response_model=TransactionGet)
async def create_transaction(
    transaction: TransactionPost,
    transaction_dao: Annotated[TransactionDAO, Depends(get_transaction)],
):
    """Create a new transaction.

    Args:
        transaction: The transaction data to create.
        transaction_dao: The transaction DAO instance.

    Raises:
        HTTPException: If the transaction data is invalid or creation fails,
            returns a 400 Bad Request error with details.

    Returns:
        The newly created transaction.

    """
    try:
        return await transaction_dao.create(transaction)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.put("/{transaction_id}", response_model=TransactionGet)
async def update_transaction(
    transaction_id: int,
    transaction: TransactionPut,
    transaction_dao: Annotated[TransactionDAO, Depends(get_transaction)],
):
    """Update an existing transaction by replacing all its fields.

    Args:
        transaction_id: The unique identifier of the transaction to update.
        transaction: The complete transaction data to replace the existing transaction.
        transaction_dao: The transaction DAO instance.

    Raises:
        HTTPException: If the transaction data is invalid or update fails,
            returns a 400 Bad Request error with details.

    Returns:
        The updated transaction.

    """
    try:
        return await transaction_dao.update(transaction_id, transaction)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.patch("/{transaction_id}", response_model=TransactionGet)
async def patch_transaction(
    transaction_id: int,
    transaction: TransactionPatch,
    transaction_dao: Annotated[TransactionDAO, Depends(get_transaction)],
):
    """Update an existing transaction by replacing only the provided fields.

    Args:
        transaction_id: The unique identifier of the transaction to update.
        transaction: The partial transaction data to update. Only provided fields
            will be updated.
        transaction_dao: The transaction DAO instance.

    """
    try:
        return await transaction_dao.modify(transaction_id, transaction)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/{transaction_id}", status_code=204)
async def delete_transaction(
    transaction_id: int,
    transaction_dao: Annotated[TransactionDAO, Depends(get_transaction)],
):
    """Delete a transaction by its ID.

    Args:
        transaction_id: The unique identifier of the transaction to delete.
        transaction_dao: The transaction DAO instance.

    Returns:
        None.

    """
    try:
        return await transaction_dao.delete(transaction_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

