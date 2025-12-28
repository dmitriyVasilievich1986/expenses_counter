"""Metadata model for the web API."""

__all__ = ("PaginationMetadata",)

from pydantic import Field

from .response import BaseResponseModel


class PaginationMetadata(BaseResponseModel):
    """Pagination and sorting metadata for list responses.

    This model provides metadata about paginated list responses, allowing clients
    to understand the current page position, total available records, and sorting
    configuration. This information is essential for implementing pagination controls
    in client applications.

    Attributes:
        total: The total number of OAuth parameter records matching the query filters.
            Used to calculate the total number of pages available.
        page: The current page number (1-indexed). Indicates which page of results
            is being returned.
        page_size: The number of items per page. Determines how many records are
            included in the current response.
        sort_by: The field name used for sorting the results (e.g., "application_id",
            "created_at"). Indicates which column the data is ordered by.
        sort_order: The sort direction, either "asc" (ascending) or "desc" (descending).
            Indicates whether results are sorted from lowest to highest or vice versa.

    Example:
        >>> metadata = PaginationMetadata(
        ...     total=150,
        ...     page=3,
        ...     page_size=20,
        ...     sort_by="application_id",
        ...     sort_order="asc"
        ... )
        >>> # This indicates: showing items 41-60 of 150 total, sorted by application_id A-Z

    """

    total: int = Field(..., description="The total number of parameters")
    offset: int = Field(..., description="The offset of the parameters")
    limit: int = Field(..., description="The limit of the parameters")
    sort_by: str = Field(..., description="The field to sort the parameters by")
    sort_order: str = Field(..., description="The order to sort the parameters by")
