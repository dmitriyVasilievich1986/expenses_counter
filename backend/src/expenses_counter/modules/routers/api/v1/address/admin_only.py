"""Admin-only HTTP API routes for shop addresses.

Provides read, create, update, and delete endpoints for addresses.
Admin access is enforced on the router via ``admin_required``. The
paginated list endpoint lives in ``all_users``.

Routes:
    GET /address/address_name/{address_name} - Single address by name
    GET /address/{address_id} - Single address by id
    POST /address - Create an address
    PUT /address/{address_id} - Replace an address
    PATCH /address/{address_id} - Partially update an address
    DELETE /address/{address_id} - Delete an address
"""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from loguru import logger
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError

from expenses_counter.modules.middlewares.dependencies import get_db
from expenses_counter.modules.middlewares.dependencies.admin_required import admin_required
from expenses_counter.modules.routers.schemas.requests.address import (
    PatchAddressBody,
    PostAddressBody,
    PutAddressBody,
)
from expenses_counter.modules.routers.schemas.responses.address import (
    GetSingleAddressResponse,
)
from expenses_counter.services.daos import AddressDAO
from expenses_counter.services.database import AsyncDatabaseClient

router = APIRouter(prefix="/address", dependencies=[Depends(admin_required)])


@router.get("/address_name/{address_name}", response_model=GetSingleAddressResponse, status_code=status.HTTP_200_OK)
async def get_address_by_local_name(
    address_name: Annotated[str, Path(description="The name of the address to retrieve")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleAddressResponse:
    """Return a single address by its address name.

    Args:
        address_name (str): Address name path segment.
        db (AsyncDatabaseClient): Database client for the request.

    Returns:
        GetSingleAddressResponse: The requested address payload.

    Raises:
        HTTPException: 404 if no address exists for ``address_name``.
        HTTPException: 500 if a database error occurs while loading the address.

    """
    address_dao = AddressDAO(database_client=db)

    try:
        payload = await address_dao.get_by_address(address_name)
    except NoResultFound as e:
        logger.warning("Address not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while retrieving the address", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while retrieving the address",
        ) from e

    return GetSingleAddressResponse.model_validate(payload)


@router.get(
    "/{address_id}",
    response_model=GetSingleAddressResponse,
    status_code=status.HTTP_200_OK,
)
async def get_address_by_id(
    address_id: Annotated[int, Path(description="The unique identifier of the address to retrieve")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleAddressResponse:
    """Return a single address by primary key.

    Args:
        address_id (int): Address primary key.
        db (AsyncDatabaseClient): Database client for the request.

    Returns:
        GetSingleAddressResponse: The requested address payload.

    Raises:
        HTTPException: 404 if no address exists for ``address_id``.
        HTTPException: 500 if a database error occurs while loading the address.

    """
    address_dao = AddressDAO(database_client=db)

    try:
        payload = await address_dao.get_by_pk(address_id)
    except NoResultFound as e:
        logger.warning("Address not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while retrieving the address", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while retrieving the address",
        ) from e

    return GetSingleAddressResponse.model_validate(payload)


@router.post(
    "",
    response_model=GetSingleAddressResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_address(
    body: Annotated[PostAddressBody, Body(description="The address data to create")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleAddressResponse:
    """Create a new address.

    Args:
        body (PostAddressBody): Fields for the new address (e.g. shop link).
        db (AsyncDatabaseClient): Database client for the request.

    Returns:
        GetSingleAddressResponse: The created address payload.

    Raises:
        HTTPException: 400 if a referenced entity violates integrity (e.g. missing shop).
        HTTPException: 500 if a database error occurs while creating the address.

    """
    address_dao = AddressDAO(database_client=db)

    try:
        payload = await address_dao.create(**body.model_dump())
    except IntegrityError as e:
        logger.exception("Related object not found", exc_info=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related object not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while creating the address", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong while creating the address"
        ) from e

    return GetSingleAddressResponse.model_validate(payload)


@router.put(
    "/{address_id}",
    response_model=GetSingleAddressResponse,
    status_code=status.HTTP_200_OK,
)
async def update_address(
    address_id: Annotated[int, Path(description="The unique identifier of the address to update")],
    body: Annotated[PutAddressBody, Body(description="The address data to update")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleAddressResponse:
    """Replace an existing address by primary key.

    Args:
        address_id (int): Address primary key.
        body (PutAddressBody): Full replacement payload for the address.
        db (AsyncDatabaseClient): Database client for the request.

    Returns:
        GetSingleAddressResponse: The updated address payload.

    Raises:
        HTTPException: 400 if a referenced entity violates integrity (e.g. invalid shop).
        HTTPException: 404 if no address exists for ``address_id``.
        HTTPException: 500 if a database error occurs while updating the address.

    """
    address_dao = AddressDAO(database_client=db)

    try:
        payload = await address_dao.update(address_id, **body.model_dump())
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

    return GetSingleAddressResponse.model_validate(payload)


@router.patch(
    "/{address_id}",
    response_model=GetSingleAddressResponse,
    status_code=status.HTTP_200_OK,
)
async def patch_address(
    address_id: Annotated[int, Path(description="The unique identifier of the address to update")],
    body: Annotated[PatchAddressBody, Body(description="The address data to update")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleAddressResponse:
    """Patch an existing address by primary key.

    Args:
        address_id (int): Address primary key.
        body (PatchAddressBody): Partial update payload for the address.
        db (AsyncDatabaseClient): Database client for the request.

    Returns:
        GetSingleAddressResponse: The updated address payload.

    Raises:
        HTTPException: 400 if a referenced entity violates integrity (e.g. invalid shop).
        HTTPException: 404 if no address exists for ``address_id``.
        HTTPException: 500 if a database error occurs while patching the address.

    """
    address_dao = AddressDAO(database_client=db)

    try:
        payload = await address_dao.update(address_id, **body.model_dump(exclude_unset=True))
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

    return GetSingleAddressResponse.model_validate(payload)


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: Annotated[int, Path(description="The unique identifier of the address to delete")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> None:
    """Delete an address by primary key.

    Args:
        address_id (int): Address primary key.
        db (AsyncDatabaseClient): Database client for the request.

    Returns:
        None

    Raises:
        HTTPException: 404 if no address exists for ``address_id``.
        HTTPException: 500 if a database error occurs while deleting the address.

    """
    address_dao = AddressDAO(database_client=db)

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
