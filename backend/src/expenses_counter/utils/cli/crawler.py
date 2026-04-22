"""Crawler commands."""

__all__ = ("crawler",)

import asyncclick as click

from expenses_counter.commands.crawl_url import CrawlAndCreateCommand


@click.group(help="Crawler commands")
async def crawler():
    """Crawler commands."""
    pass


@crawler.command(help="Crawl and create transaction")
@click.option("--url", help="URL to crawl", required=True)
@click.option("--default-category-id", help="Default category ID", type=int, required=False, default=None)
async def crawl_and_create(url: str, default_category_id: int | None):
    """Crawl and create transaction."""
    command = CrawlAndCreateCommand(url=url, default_category_id=default_category_id)
    await command.initialize()
    await command.validate()
    await command.execute()
