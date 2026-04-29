"""Catch-all HTTP routes that serve the single-page application shell."""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Depends, Path
from fastapi.responses import FileResponse

from expenses_counter.config import AppConfig
from expenses_counter.modules.middlewares.dependencies import get_config

router = APIRouter()


@router.get("/{_path:path}", include_in_schema=False)
async def spa_fallback(
    _path: Annotated[
        str,
        Path(
            ...,
            description="Request path segment (unused; accepted for catch-all routing)",
        ),
    ],
    app_config: Annotated[AppConfig, Depends(get_config)],
) -> FileResponse:
    """Return ``index.html`` for any path so the client router can handle URLs.

    Args:
        _path (str): Matched path; not read, only satisfies routing.
        app_config (AppConfig): Application configuration (resolved static paths).

    Returns:
        FileResponse: The SPA entry HTML file from configured ``paths_info``.

    """
    index_html = app_config.info.paths_info.index_html
    return FileResponse(index_html)
