"""Get popular products query schema module."""

__all__ = ("GetPopularProductsQuery",)


from pydantic import Field

from expenses_counter.modules.routers.schemas.base.query import BaseQueryModel


class GetPopularProductsQuery(BaseQueryModel):
    """Query parameters for getting popular products."""

    limit: int = Field(default=10, ge=1, le=100, description="The number of products to return")
