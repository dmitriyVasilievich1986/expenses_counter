"""CLI subcommands for user creation, password checks, and JWT tokens."""

__all__ = ("user",)

import asyncclick as click

from expenses_counter.config import AppConfig
from expenses_counter.services.auth import JWTTokenService, PasswordService
from expenses_counter.services.daos import UserDAO
from expenses_counter.services.database import AsyncDatabaseClient


@click.group(help="User commands", name="user")
@click.pass_context
async def user(ctx: click.Context):
    """Nest user-related commands and attach the DB client and UserDAO to context.

    Args:
        ctx (click.Context): Click context whose ``obj`` must include ``config``.

    Returns:
        None

    """
    app_config = ctx.obj["config"]
    db = AsyncDatabaseClient(app_config)
    ctx.obj["db"] = db
    ctx.obj["user_dao"] = UserDAO(db)


@user.command(help="Create a user")
@click.option("--username", help="Username", required=True)
@click.option("--email", help="Email", required=True)
@click.option("--password", help="Password", required=True, prompt=True, hide_input=True)
@click.pass_context
async def create_user(ctx: click.Context, username: str, email: str, password: str):
    """Create a new user with hashed credentials and print the result.

    Args:
        ctx (click.Context): Click context with ``user_dao`` from the ``user`` group.
        username (str): Unique login name.
        email (str): Email address stored for the user.
        password (str): Plain password; stored hashed via the DAO. Prompted if not provided.

    Returns:
        None

    """
    user_dao: UserDAO = ctx.obj["user_dao"]
    user = await user_dao.create(username=username, email=email, password=password)
    click.echo(f"User created: {user}")


@user.command(help="Check password")
@click.option("--username", help="Username", required=True)
@click.option("--password", help="Password", required=True, prompt=True, hide_input=True)
@click.pass_context
async def check_password(ctx: click.Context, username: str, password: str):
    """Verify a plaintext password against the stored hash for a username.

    Args:
        ctx (click.Context): Click context with ``user_dao`` and ``config``.
        username (str): User whose stored hash is checked.
        password (str): Plain password to verify. Prompted if not provided.

    Returns:
        None

    """
    user_dao: UserDAO = ctx.obj["user_dao"]
    user = await user_dao.get_by_username(username)

    if PasswordService.check_password(password, user.password):
        click.echo("Password is correct")
    else:
        click.echo("Password is incorrect")


@user.command(help="Generate JWT token")
@click.option("--username", help="Username", required=True)
@click.pass_context
async def generate_jwt_token(ctx: click.Context, username: str):
    """Issue an access JWT for the user identified by username and print it.

    Args:
        ctx (click.Context): Click context with ``user_dao`` and ``config``.
        username (str): User to embed in the token subject.

    Returns:
        None

    """
    user_dao: UserDAO = ctx.obj["user_dao"]
    app_config: AppConfig = ctx.obj["config"]
    user = await user_dao.get_by_username(username)
    jwt_token_service = JWTTokenService(app_config.services.auth.jwt_secret_key.get_secret_value())
    jwt_token = jwt_token_service.generate_token(user.id)
    click.echo(f"JWT token: {jwt_token}")


@user.command(help="Re-generate password hash")
@click.option("--username", help="Username", required=True)
@click.option("--password", help="Password", required=True, prompt=True, hide_input=True)
@click.pass_context
async def re_generate_password(ctx: click.Context, username: str, password: str):
    """Re-generate the password hash for a user.

    Args:
        ctx (click.Context): Click context with ``user_dao`` and ``config``.
        username (str): User to re-generate the password hash for.
        password (str): Password to use to re-generate the password hash.

    Returns:
        None

    """
    user_dao: UserDAO = ctx.obj["user_dao"]
    user = await user_dao.get_by_username(username)
    hashed_password = PasswordService.hash_password(password)
    await user_dao.update(pk=user.id, password=hashed_password)
    click.echo(f"Password hash re-generated for user {username}")
