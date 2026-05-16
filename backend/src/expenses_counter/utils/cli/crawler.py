"""CLI subcommands for crawling URLs and persisting extracted expense data."""

__all__ = ("crawler",)

import asyncclick as click

from expenses_counter.commands.crawl_url import CreateTransactionsFromCrawledDataCommand
from expenses_counter.config import AppConfig
from expenses_counter.services.daos import UserDAO
from expenses_counter.services.database import AsyncDatabaseClient
from expenses_counter.utils.web_crawler import Crawler


@click.group(help="Crawler commands")
async def crawler() -> None:
    """Group CLI commands for web crawling.

    Returns:
        None

    """
    pass


@crawler.command(help="Crawl URL")
@click.option("--url", help="URL to crawl", required=True)
async def crawl_url(url: str) -> None:
    """Fetch and parse a URL, then write the extracted data to stdout.

    Args:
        url (str): Page URL to pass to the crawler.

    Returns:
        None

    """
    crawler = Crawler(url=url)
    data = crawler.run()
    click.echo(data)


@crawler.command(help="Crawl and create transaction")
@click.option("--url", help="URL to crawl", required=True)
@click.option("--username", help="Username", type=str, required=True)
@click.pass_context
async def crawl_and_create(
    ctx: click.Context,
    url: str,
    username: str,
) -> None:
    """Crawl a URL and create database records from the parsed result.

    Loads app configuration from the parent CLI context, loads a user with
    ``UserDAO.get_by_username``, then runs ``CreateTransactionsFromCrawledDataCommand`` to validate
    and persist transactions.

    Args:
        ctx (click.Context): Parent CLI context with ``config`` (``AppConfig``).
        url (str): Page URL to crawl.
        username (str): Value forwarded to ``get_by_username`` to load the acting user.

    Returns:
        None

    """
    crawler = Crawler(url=url)
    data = crawler.run()

    app_config: AppConfig = ctx.obj["config"]
    db_client = AsyncDatabaseClient(app_config=app_config)
    user_dao = UserDAO(db_client)
    user = await user_dao.get_by_username(username)

    cmd = CreateTransactionsFromCrawledDataCommand(data=data, user=user, db=db_client)
    await cmd.initialize()
    await cmd.validate()
    await cmd.execute()
