"""Shop router module."""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from expenses_counter.services.daos import ShopDAO
from expenses_counter.services.daos.shop.schemas import (
    ShopGet,
    ShopPatch,
    ShopPost,
    ShopPut,
)
from expenses_counter.modules.middlewares.dependencies import get_shop

router = APIRouter(prefix="/shop", tags=["Shop"])


@router.get("", response_model=list[ShopGet])
async def get_shop_list(
    shop_dao: Annotated[ShopDAO, Depends(get_shop)],
):
    """Retrieve all shops.

    Args:
        shop_dao: The shop DAO instance.

    Returns:
        A list of all shops in the system.

    """
    return await shop_dao.get_all()


@router.get("/{shop_id}", response_model=ShopGet)
async def get_shop_by_id(
    shop_id: int,
    shop_dao: Annotated[ShopDAO, Depends(get_shop)],
):
    """Retrieve a shop by its ID.

    Args:
        shop_id: The unique identifier of the shop to retrieve.
        shop_dao: The shop DAO instance.

    """
    shop = await shop_dao.get_by_id(shop_id)
    if shop is None:
        raise HTTPException(status_code=404, detail="Shop not found")
    return shop


@router.post("", response_model=ShopGet)
async def create_shop(
    shop: ShopPost,
    shop_dao: Annotated[ShopDAO, Depends(get_shop)],
):
    """Create a new shop.

    Args:
        shop: The shop data to create.
        shop_dao: The shop DAO instance.

    Raises:
        HTTPException: If the shop data is invalid or creation fails,
            returns a 400 Bad Request error with details.

    Returns:
        The newly created shop.

    """
    try:
        return await shop_dao.create(shop)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.put("/{shop_id}", response_model=ShopGet)
async def update_shop(
    shop_id: int,
    shop: ShopPut,
    shop_dao: Annotated[ShopDAO, Depends(get_shop)],
):
    """Update an existing shop by replacing all its fields.

    Args:
        shop_id: The unique identifier of the shop to update.
        shop: The complete shop data to replace the existing shop.
        shop_dao: The shop DAO instance.

    Raises:
        HTTPException: If the shop data is invalid or update fails,
            returns a 400 Bad Request error with details.

    Returns:
        The updated shop.

    """
    try:
        return await shop_dao.update(shop_id, shop)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.patch("/{shop_id}", response_model=ShopGet)
async def patch_shop(
    shop_id: int,
    shop: ShopPatch,
    shop_dao: Annotated[ShopDAO, Depends(get_shop)],
):
    """Update an existing shop by replacing only the provided fields.

    Args:
        shop_id: The unique identifier of the shop to update.
        shop: The partial shop data to update. Only provided fields
            will be updated.
        shop_dao: The shop DAO instance.

    """
    try:
        return await shop_dao.modify(shop_id, shop)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/{shop_id}", status_code=204)
async def delete_shop(
    shop_id: int,
    shop_dao: Annotated[ShopDAO, Depends(get_shop)],
):
    """Delete a shop by its ID.

    Args:
        shop_id: The unique identifier of the shop to delete.
        shop_dao: The shop DAO instance.

    Returns:
        None.

    """
    try:
        return await shop_dao.delete(shop_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
