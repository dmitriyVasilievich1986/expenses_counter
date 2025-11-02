"""API router module."""

__all__ = ("router",)

from fastapi import APIRouter

router = APIRouter(prefix="/api")
