"""Address API router module.

REST endpoints for reading, creating, updating, and deleting addresses, including
pagination for list responses and lookup by id or by local name.

Routes:
    GET /address - List addresses with pagination
    GET /address/name/{local_name} - Get an address by local name
    GET /address/{address_id} - Get an address by id
    POST /address - Create an address
    PUT /address/{address_id} - Full replace of an address
    PATCH /address/{address_id} - Partial update of an address
    DELETE /address/{address_id} - Delete an address
"""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from loguru import logger
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError

from expenses_counter.modules.middlewares.dependencies.daos.get_address import get_address
from expenses_counter.modules.routers.schemas.base.metadata import PaginationMetadata
from expenses_counter.modules.routers.schemas.requests.address import (
    GetAllAddressesQuery,
    PatchAddressBody,
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


@router.get("", response_model=GetAllAddressesResponse, status_code=status.HTTP_200_OK)
async def get_address_list(
    address_dao: Annotated[AddressDAO, Depends(get_address)],
    query: Annotated[GetAllAddressesQuery, Query(description="Pagination and sorting parameters")],
) -> GetAllAddressesResponse:
    """Return a paginated list of addresses.

    Args:
        address_dao (AddressDAO): Injected address data access object.
        query (GetAllAddressesQuery): Pagination and sort query parameters.

    Returns:
        GetAllAddressesResponse: List items and pagination metadata.

    Raises:
        HTTPException: 500 if listing addresses fails due to a database error.

    """
    try:
        data, total = await address_dao.get_all(**query.model_dump())
        metadata = PaginationMetadata(total=total, **query.model_dump())
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while retrieving the address list", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while retrieving the address list",
        ) from e

    return GetAllAddressesResponse(
        data=[SimpleAddressGet.model_validate(address) for address in data], metadata=metadata
    )


@router.get("/name/{local_name}", response_model=GetSingleAddressResponse, status_code=status.HTTP_200_OK)
async def get_address_by_local_name(
    local_name: Annotated[str, Path(description="The local name of the address to retrieve")],
    address_dao: Annotated[AddressDAO, Depends(get_address)],
) -> GetSingleAddressResponse:
    """Return a single address identified by its local name.

    Args:
        local_name (str): Address local name path segment.
        address_dao (AddressDAO): Injected address data access object.

    Returns:
        GetSingleAddressResponse: The matching address.

    Raises:
        HTTPException: 404 if no address exists for that name, or 500 on database error.

    """
    try:
        return await address_dao.get_by_address(local_name)
    except NoResultFound as e:
        logger.warning("Address not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while retrieving the address", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while retrieving the address",
        ) from e


@router.get("/{address_id}", response_model=GetSingleAddressResponse, status_code=status.HTTP_200_OK)
async def get_address_by_id(
    address_id: Annotated[int, Path(description="The unique identifier of the address to retrieve")],
    address_dao: Annotated[AddressDAO, Depends(get_address)],
) -> GetSingleAddressResponse:
    """Return a single address by primary key.

    Args:
        address_id (int): Address id path parameter.
        address_dao (AddressDAO): Injected address data access object.

    Returns:
        GetSingleAddressResponse: The matching address.

    Raises:
        HTTPException: 404 if the id is unknown, or 500 on database error.

    """
    try:
        return await address_dao.get_by_pk(address_id)
    except NoResultFound as e:
        logger.warning("Address not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while retrieving the address", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while retrieving the address",
        ) from e


@router.post("", response_model=GetSingleAddressResponse, status_code=status.HTTP_201_CREATED)
async def create_address(
    body: Annotated[PostAddressBody, Body(description="The address data to create")],
    address_dao: Annotated[AddressDAO, Depends(get_address)],
) -> GetSingleAddressResponse:
    """Create a new address and return the persisted row.

    Args:
        body (PostAddressBody): New address fields.
        address_dao (AddressDAO): Injected address data access object.

    Returns:
        GetSingleAddressResponse: The created address.

    Raises:
        HTTPException: 400 if a related entity is missing (integrity), or 500 on
            other database errors.

    """
    try:
        return await address_dao.create(**body.model_dump())
    except IntegrityError as e:
        logger.exception("Related object not found", exc_info=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related object not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while creating the address", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong while creating the address"
        ) from e


@router.put("/{address_id}", response_model=GetSingleAddressResponse, status_code=status.HTTP_200_OK)
async def update_address(
    address_id: Annotated[int, Path(description="The unique identifier of the address to update")],
    body: Annotated[PutAddressBody, Body(description="The address data to update")],
    address_dao: Annotated[AddressDAO, Depends(get_address)],
) -> GetSingleAddressResponse:
    """Replace an address with the request body (full update).

    Args:
        address_id (int): Address id path parameter.
        body (PutAddressBody): Full replacement address payload.
        address_dao (AddressDAO): Injected address data access object.

    Returns:
        GetSingleAddressResponse: The updated address.

    Raises:
        HTTPException: 400 if a related entity is missing (integrity), 404 if the
            id is unknown, or 500 on other database errors.

    """
    try:
        r = await address_dao.update(address_id, **body.model_dump())
        return GetSingleAddressResponse.model_validate(r)
    except IntegrityError as e:
        logger.exception("Related object not found", exc_info=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related object not found") from e
    except NoResultFound as e:
        logger.warning("Address not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while updating the address", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong while updating the address"
        ) from e


@router.patch("/{address_id}", response_model=GetSingleAddressResponse, status_code=status.HTTP_200_OK)
async def patch_address(
    address_id: Annotated[int, Path(description="The unique identifier of the address to update")],
    body: Annotated[PatchAddressBody, Body(description="The address data to update")],
    address_dao: Annotated[AddressDAO, Depends(get_address)],
) -> GetSingleAddressResponse:
    """Update only the fields present in the request (partial update).

    Args:
        address_id (int): Address id path parameter.
        body (PatchAddressBody): Fields to apply; unset fields are left unchanged.
        address_dao (AddressDAO): Injected address data access object.

    Returns:
        GetSingleAddressResponse: The updated address.

    Raises:
        HTTPException: 400 if a related entity is missing (integrity), 404 if the
            id is unknown, or 500 on other database errors.

    """
    try:
        return await address_dao.update(address_id, **body.model_dump(exclude_unset=True))
    except IntegrityError as e:
        logger.exception("Related object not found", exc_info=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related object not found") from e
    except NoResultFound as e:
        logger.warning("Address not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while updating the address", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong while updating the address"
        ) from e


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: Annotated[int, Path(description="The unique identifier of the address to delete")],
    address_dao: Annotated[AddressDAO, Depends(get_address)],
) -> None:
    """Delete an address by id.

    Args:
        address_id (int): Address id path parameter.
        address_dao (AddressDAO): Injected address data access object.

    Returns:
        None: Empty response body with 204 No Content on success.

    Raises:
        HTTPException: 404 if the id is unknown, or 500 on database error.

    """
    try:
        await address_dao.delete(address_id)
    except NoResultFound as e:
        logger.warning("Address not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while deleting the address", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong while deleting the address"
        ) from e
