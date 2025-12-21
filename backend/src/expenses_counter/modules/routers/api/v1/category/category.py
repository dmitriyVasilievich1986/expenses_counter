"""Category API router module.

This module provides REST API endpoints for managing categories in the expenses
counter application. It includes endpoints for listing, retrieving, creating,
updating, and deleting categories.
"""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from expenses_counter.services.daos.category import CategoryDAO
from expenses_counter.services.daos.category.schemas import (
    CategoryGet,
    CategoryPatch,
    CategoryPost,
    CategoryPut,
)
from expenses_counter.modules.middlewares.dependencies import get_category

router = APIRouter(prefix="/category", tags=["Category"])


@router.get("", response_model=list[CategoryGet])
async def get_category_list(
    category_dao: Annotated[CategoryDAO, Depends(get_category)],
):
    """Retrieve all categories.

    Args:
        category_dao: The category DAO instance.

    Returns:
        A list of all categories in the system.

    """
    return await category_dao.get_all()


@router.get("/{category_id}", response_model=CategoryGet)
async def get_category_by_id(
    category_id: int,
    category_dao: Annotated[CategoryDAO, Depends(get_category)],
):
    """Retrieve a category by its ID.

    Args:
        category_id: The unique identifier of the category to retrieve.
        category_dao: The category DAO instance.

    Raises:
        HTTPException: If the category with the given ID is not found,
            returns a 404 Not Found error.

    Returns:
        The category with the specified ID.

    """
    category = await category_dao.get_by_id(category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("", response_model=CategoryGet)
async def create_category(
    category: CategoryPost,
    category_dao: Annotated[CategoryDAO, Depends(get_category)],
):
    """Create a new category.

    Args:
        category: The category data to create.
        category_dao: The category DAO instance.

    Raises:
        HTTPException: If the category data is invalid or creation fails,
            returns a 400 Bad Request error with details.

    Returns:
        The newly created category.

    """
    try:
        return await category_dao.create(category)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.put("/{category_id}", response_model=CategoryGet)
async def update_category(
    category_id: int,
    category: CategoryPut,
    category_dao: Annotated[CategoryDAO, Depends(get_category)],
):
    """Update an existing category by replacing all its fields.

    Args:
        category_id: The unique identifier of the category to update.
        category: The complete category data to replace the existing category.
        category_dao: The category DAO instance.

    Raises:
        HTTPException: If the category data is invalid or update fails,
            returns a 400 Bad Request error with details.

    Returns:
        The updated category.

    """
    try:
        category = await category_dao.update(category_id, category)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return category


@router.patch("/{category_id}", response_model=CategoryGet)
async def patch_category(
    category_id: int,
    category: CategoryPatch,
    category_dao: Annotated[CategoryDAO, Depends(get_category)],
):
    """Partially update an existing category.

    Args:
        category_id: The unique identifier of the category to update.
        category: The partial category data to update. Only provided fields
            will be updated.
        category_dao: The category DAO instance.

    Raises:
        HTTPException: If the category data is invalid or update fails,
            returns a 400 Bad Request error with details.

    Returns:
        The updated category.

    """
    try:
        category = await category_dao.modify(category_id, category)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return category


@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: int,
    category_dao: Annotated[CategoryDAO, Depends(get_category)],
):
    """Delete a category by its ID.

    Args:
        category_id: The unique identifier of the category to delete.
        category_dao: The category DAO instance.

    Returns:
        No content (204 status code) on successful deletion.

    """
    await category_dao.delete(category_id)
