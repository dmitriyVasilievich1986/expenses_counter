"""Crawl transaction body schema module."""

__all__ = ("CrawlTransactionBody",)

from pydantic import Field

from expenses_counter.modules.routers.schemas.base.request import BaseRequestModel


class CrawlTransactionBody(BaseRequestModel):
    """Request body for crawling a transaction."""

    url: str = Field(..., description="The url of the transaction to crawl")
