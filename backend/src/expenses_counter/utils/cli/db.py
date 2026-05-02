"""Database CLI subcommands for schema migrations and seed data."""

import asyncio

import asyncclick as click
from alembic import command
from alembic.config import Config

from expenses_counter.commands.fill_db import FillDBCommand
from expenses_counter.config import AppConfig


@click.group(help="Database commands")
async def db():
    """Expose database maintenance commands as a nested CLI group.

    Returns:
        None

    """
    pass


@db.command(help="Migrate the database using Alembic.")
@click.pass_context
@click.option("--revision", help="The revision to migrate to.", default="head")
async def migrate_db(ctx: click.Context, revision: str) -> None:
    """Upgrade the database schema to the latest Alembic revision.

    Args:
        ctx (click.Context): Click context holding ``config`` with paths to Alembic.
        revision (str): The revision to migrate to. Defaults to "head".

    Returns:
        None

    """
    config: AppConfig = ctx.obj["config"]
    alembic_config = Config(config.info.paths_info.alembic_ini)
    await asyncio.to_thread(command.upgrade, alembic_config, revision)


@db.command(help="Downgrade the database using Alembic.")
@click.pass_context
@click.option("--revision", help="The revision to downgrade to.", default="base")
async def downgrade_db(ctx: click.Context, revision: str) -> None:
    """Downgrade the database schema to the specified Alembic revision.

    Args:
        ctx (click.Context): Click context holding ``config`` with paths to Alembic.
        revision (str): The revision to downgrade to.

    Returns:
        None

    """
    config: AppConfig = ctx.obj["config"]
    alembic_config = Config(config.info.paths_info.alembic_ini)
    await asyncio.to_thread(command.downgrade, alembic_config, revision)


@db.command(help="Fill the database with initial data.")
@click.pass_context
async def fill_db(ctx: click.Context) -> None:
    """Insert the sample expense graph produced by ``FillDBCommand``.

    Args:
        ctx (click.Context): Click context holding ``config`` for database access.

    Returns:
        None

    """
    config: AppConfig = ctx.obj["config"]
    cmd = FillDBCommand(app_config=config)
    await cmd.initialize()
    await cmd.validate()
    await cmd.execute()
    click.echo("Database filled with initial data.")
