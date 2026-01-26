"""Address API router module.

This module provides REST API endpoints for managing addresses in the expenses
counter application. It includes full CRUD (Create, Read, Update, Delete) operations
for addresses with support for shop relationships.

The router handles:
    - Listing addresses with pagination and sorting
    - Retrieving individual addresses with shop information
    - Creating new addresses with required shop relationships
    - Updating existing addresses
    - Deleting addresses

All endpoints include proper error handling for database exceptions and return
appropriate HTTP status codes.

Routes:
    GET /address - List all addresses with pagination
    GET /address/{address_id} - Get a single address by ID
    POST /address - Create a new address
    PUT /address/{address_id} - Update an existing address
    DELETE /address/{address_id} - Delete an address
"""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.exc import DatabaseError, IntegrityError, NoResultFound

from expenses_counter.modules.middlewares.dependencies import get_address
from expenses_counter.modules.routers.schemas.base.metadata import PaginationMetadata
from expenses_counter.modules.routers.schemas.requests.address import (
    GetAllAddressesQuery,
    PostAddressBody,
    PutAddressBody,
)
from expenses_counter.modules.routers.schemas.responses.address import (
    GetAllAddressesResponse,
    GetSingleAddressResponse,
    SimpleAddressGet,
)
from expenses_counter.services.daos import AddressDAO

router = APIRouter(prefix="/address", tags=["Address"])


@router.get("", response_model=GetAllAddressesResponse)
async def get_address_list(
    address_dao: Annotated[AddressDAO, Depends(get_address)],
    query: Annotated[GetAllAddressesQuery, Query(description="Pagination and sorting parameters")],
):
    """Retrieve all addresses with pagination and sorting.

    Args:
        address_dao: The address DAO instance.
        query: Pagination and sorting parameters including limit, offset, sort_by, and sort_order.

    Returns:
        GetAllAddressesResponse containing a list of addresses and pagination metadata.

    Raises:
        HTTPException: If retrieval fails, returns a 500 Internal Server Error.

    """
    try:
        data, total = await address_dao.get_all(
            limit=query.limit, offset=query.offset, sort_by=query.sort_by, sort_order=query.sort_order
        )
        metadata = PaginationMetadata(
            total=total, offset=query.offset, limit=query.limit, sort_by=query.sort_by, sort_order=query.sort_order
        )
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Something went wrong while retrieving the address list") from e

    return GetAllAddressesResponse(
        data=[SimpleAddressGet.model_validate(address) for address in data], metadata=metadata
    )


@router.get("/{address_id}", response_model=GetSingleAddressResponse)
async def get_address_by_id(
    address_id: Annotated[int, Path(description="The unique identifier of the address to retrieve")],
    address_dao: Annotated[AddressDAO, Depends(get_address)],
):
    """Retrieve an address by its ID.

    Args:
        address_id: The unique identifier of the address to retrieve.
        address_dao: The address DAO instance.

    Returns:
        GetSingleAddressResponse containing the address details.

    Raises:
        HTTPException: If the address is not found, returns a 404 Not Found error.
            If retrieval fails, returns a 500 Internal Server Error.

    """
    try:
        address = await address_dao.get_by_id(address_id)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Something went wrong while retrieving the address") from e

    if address is None:
        raise HTTPException(status_code=404, detail="Address not found")

    return address


@router.post("", response_model=GetSingleAddressResponse)
async def create_address(
    body: PostAddressBody,
    address_dao: Annotated[AddressDAO, Depends(get_address)],
):
    """Create a new address.

    Args:
        body: The address data to create including local_name, address, and shop_id.
        address_dao: The address DAO instance.

    Returns:
        GetSingleAddressResponse containing the newly created address.

    Raises:
        HTTPException: If the referenced shop is not found, returns a 400 Bad Request error.
            If creation fails, returns a 500 Internal Server Error.

    """
    try:
        return await address_dao.create(**body.model_dump(by_alias=False))
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="Shop not found") from e
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Something went wrong while creating the address") from e


@router.put("/{address_id}", response_model=GetSingleAddressResponse)
async def update_address(
    address_id: Annotated[int, Path(description="The unique identifier of the address to update")],
    body: PutAddressBody,
    address_dao: Annotated[AddressDAO, Depends(get_address)],
):
    """Update an existing address by replacing all its fields.

    Args:
        address_id: The unique identifier of the address to update.
        body: The complete address data to replace the existing address.
        address_dao: The address DAO instance.

    Returns:
        GetSingleAddressResponse containing the updated address.

    Raises:
        HTTPException: If the referenced shop is not found, returns a 400 Bad Request error.
            If the address is not found, returns a 404 Not Found error.
            If update fails, returns a 500 Internal Server Error.

    """
    try:
        return await address_dao.update(address_id, **body.model_dump(by_alias=False))
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="Shop not found") from e
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail="Address not found") from e
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Something went wrong while updating the address") from e


@router.delete("/{address_id}", status_code=204)
async def delete_address(
    address_id: Annotated[int, Path(description="The unique identifier of the address to delete")],
    address_dao: Annotated[AddressDAO, Depends(get_address)],
):
    """Delete an address by its ID.

    Args:
        address_id: The unique identifier of the address to delete.
        address_dao: The address DAO instance.

    Returns:
        None (204 No Content status code).

    Raises:
        HTTPException: If the address is not found, returns a 404 Not Found error.
            If deletion fails, returns a 500 Internal Server Error.

    """
    try:
        deleted = await address_dao.delete(address_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Address not found")
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail="Address not found") from e
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Something went wrong while deleting the address") from e
