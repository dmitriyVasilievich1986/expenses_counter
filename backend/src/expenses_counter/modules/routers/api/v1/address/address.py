from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from expenses_counter.services.daos.address import AddressDAO
from expenses_counter.services.daos.address.schemas import (
    AddressGet,
    AddressPatch,
    AddressPost,
    AddressPut,
)
from expenses_counter.modules.middlewares.dependencies import get_address

router = APIRouter(prefix="/address", tags=["Address"])


@router.get("", response_model=list[AddressGet])
async def get_address_list(
    address_dao: Annotated[AddressDAO, Depends(get_address)],
):
    """Retrieve all addresses.

    Args:
        address_dao: The address DAO instance.

    Returns:
        A list of all addresses in the system.

    """
    return await address_dao.get_all()


@router.get("/{address_id}", response_model=AddressGet)
async def get_address_by_id(
    address_id: int,
    address_dao: Annotated[AddressDAO, Depends(get_address)],
):
    """Retrieve an address by its ID.

    Args:
        address_id: The unique identifier of the address to retrieve.
        address_dao: The address DAO instance.

    """
    address = await address_dao.get_by_id(address_id)
    if address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    return address


@router.post("", response_model=AddressGet)
async def create_address(
    address: AddressPost,
    address_dao: Annotated[AddressDAO, Depends(get_address)],
):
    """Create a new address.

    Args:
        address: The address data to create.
        address_dao: The address DAO instance.

    """
    try:
        return await address_dao.create(address)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.put("/{address_id}", response_model=AddressGet)
async def update_address(
    address_id: int,
    address: AddressPut,
    address_dao: Annotated[AddressDAO, Depends(get_address)],
):
    """Update an existing address by replacing all its fields.

    Args:
        address_id: The unique identifier of the address to update.
        address: The complete address data to replace the existing address.
        address_dao: The address DAO instance.

    """
    try:
        return await address_dao.update(address_id, address)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.patch("/{address_id}", response_model=AddressGet)
async def patch_address(
    address_id: int,
    address: AddressPatch,
    address_dao: Annotated[AddressDAO, Depends(get_address)],
):
    """Update an existing address by partially replacing its fields.

    Args:
        address_id: The unique identifier of the address to update.
        address: The partial address data to replace the existing address.
        address_dao: The address DAO instance.

    """
    try:
        return await address_dao.modify(address_id, address)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/{address_id}", status_code=204)
async def delete_address(
    address_id: int,
    address_dao: Annotated[AddressDAO, Depends(get_address)],
):
    """Delete an existing address.

    Args:
        address_id: The unique identifier of the address to delete.
        address_dao: The address DAO instance.

    """
    try:
        await address_dao.delete(address_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
