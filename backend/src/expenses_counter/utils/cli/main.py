"""Main CLI module."""

__all__ = ("main",)

import asyncclick as click
import uvicorn

from expenses_counter import __version__ as app_version
from expenses_counter.config import AppConfig

from .crawler import crawler
from .db import db


@click.group(help="CLI for managing the Expenses Counter.")
@click.version_option(app_version, "-v", "--version", message=f"Expenses Counter, version {app_version}")
@click.pass_context
async def main(ctx: click.Context) -> None:
    """Initialize the main CLI group for the Expenses Counter.

    This function serves as the root command group for all CLI operations.
    It initializes the application settings and stores them in the Click
    context for use by subcommands.

    Args:
        ctx: Click context object for sharing data between commands.

    Returns:
        None

    """
    ctx.ensure_object(dict)
    ctx.obj["config"] = AppConfig.get_or_create()


@main.command(help="Show the Expenses Counter application configuration.")
@click.pass_context
async def show_config(ctx: click.Context) -> None:
    """Print the resolved application configuration as indented JSON.

    Args:
        ctx (click.Context): Click context holding the loaded ``AppConfig``.

    Returns:
        None

    """
    config: AppConfig = ctx.obj["config"]
    click.echo(config.model_dump_json(indent=2))


@main.command(help="Start the Expenses Counter application server.")
@click.option("--host", default="0.0.0.0", help="Host to bind the server to.")
@click.option("--port", default=8000, help="Port to bind the server to.")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development.")
def run(host: str, port: int, reload: bool) -> None:
    """Start the Expenses Counter web server using Uvicorn.

    Launches the FastAPI application server with the specified configuration.
    The server can be run in development mode with auto-reload enabled for
    rapid iteration.

    Args:
        host: The network interface to bind the server to (default: "0.0.0.0").
        port: The port number to listen on (default: 8000).
        reload: Enable auto-reload when code changes are detected (default: False).

    Returns:
        None

    """
    click.echo(f"Starting Expenses Counter on {host}:{port} (reload={reload})")
    uvicorn.run(
        "expenses_counter.modules.app:get_app",
        host=host,
        port=port,
        reload=reload,
        factory=True,
    )


main.add_command(crawler)
main.add_command(db)
