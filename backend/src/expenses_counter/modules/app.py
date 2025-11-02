"""FastAPI application factory module.

This module provides the application factory function that creates and configures
the FastAPI application instance with all necessary middleware, routers, and settings.
"""

__all__ = ("get_app",)

from fastapi import FastAPI
from loguru import logger

from expenses_counter import __version__ as app_version
from expenses_counter.config.app_config import AppConfig
from expenses_counter.modules.middlewares.app_lifespan import lifespan

from .routers.api import router as root_router
from .routers.system import router as system_router


def get_app(config: AppConfig | None = None) -> FastAPI:
    """Create and configure a FastAPI application instance.

    This function initializes a FastAPI application with the provided configuration,
    sets up the application title, description, version, debug mode, and log level.
    It also includes the system router and sets up the application lifespan context.

    Args:
        config: Optional application configuration. If not provided, the default
            AppConfig instance will be retrieved or created.

    Returns:
        A fully configured FastAPI application instance ready to be run.

    """
    logger.info("Getting app...")
    config = config or AppConfig.get_or_create()
    logger.debug(f"Config: {config}")

    logger.debug("Creating FastAPI app...")
    app = FastAPI(
        title=config.name,
        description=config.description,
        version=app_version,
        debug=config.debug,
        log_level=config.app_log_level,
        lifespan=lifespan,
    )
    logger.debug("Adding system router...")
    app.include_router(system_router)

    logger.debug("Adding root router...")
    app.include_router(root_router)

    logger.info("App created successfully.")
    return app
