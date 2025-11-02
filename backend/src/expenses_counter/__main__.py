"""Main entry point for the expenses counter application.

This module provides the main entry point that initializes the FastAPI application
and runs it using uvicorn ASGI server.
"""

import uvicorn

from expenses_counter.config.app_config import AppConfig
from expenses_counter.modules.app import get_app


def main():
    """Initialize and run the FastAPI application.

    This function retrieves the application configuration, creates the FastAPI
    app instance, and starts the uvicorn server with the configured host, port,
    and log level.
    """
    config = AppConfig.get_or_create()

    app = get_app(config=config)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=config.app_port,
        log_level=config.app_log_level.lower(),
    )


if __name__ == "__main__":
    main()
