"""Crawler commands."""

__all__ = ("crawler",)

import asyncio

import click

from expenses_counter.commands.crawl_url import CrawlAndCreateCommand


@click.group(help="Crawler commands")
def crawler():
    """Crawler commands."""
    pass


@crawler.command(help="Crawl and create transaction")
@click.option("--url", help="URL to crawl", required=True)
@click.option("--default-category-id", help="Default category ID", type=int, required=False, default=None)
def crawl_and_create(url: str, default_category_id: int | None):
    """Crawl and create transaction."""

    async def create():
        command = CrawlAndCreateCommand(url=url, default_category_id=default_category_id)
        await command.initialize()
        await command.validate()
        await command.execute()

    asyncio.run(create())
