"""Authenticated HTTP API routes for shop addresses.

Provides the paginated address list for any authenticated user.
Access is enforced on the router via ``user_authorized``. Admin-only
mutating and single-item read routes live in ``admin_only``.

Routes:
    GET /address - Paginated address list
"""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

from expenses_counter.modules.middlewares.dependencies import get_db
from expenses_counter.modules.middlewares.dependencies.user_authorized import user_authorized
from expenses_counter.modules.routers.schemas.base.metadata import PaginationMetadata
from expenses_counter.modules.routers.schemas.requests.address import (
    GetAllAddressesQuery,
)
from expenses_counter.modules.routers.schemas.responses.address import (
    GetAllAddressesResponse,
    SimpleAddressGet,
)
from expenses_counter.services.daos import AddressDAO
from expenses_counter.services.database import AsyncDatabaseClient

router = APIRouter(prefix="/address", dependencies=[Depends(user_authorized)])


@router.get("", response_model=GetAllAddressesResponse, status_code=status.HTTP_200_OK)
async def get_address_list(
    query: Annotated[GetAllAddressesQuery, Query(description="Pagination and sorting parameters")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetAllAddressesResponse:
    """Return all addresses with pagination metadata.

    Args:
        query (GetAllAddressesQuery): Pagination and sort parameters.
        db (AsyncDatabaseClient): Database client for the request.

    Returns:
        GetAllAddressesResponse: Addresses and pagination metadata.

    Raises:
        HTTPException: 500 if a database error occurs while listing addresses.

    """
    address_dao = AddressDAO(database_client=db)

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
