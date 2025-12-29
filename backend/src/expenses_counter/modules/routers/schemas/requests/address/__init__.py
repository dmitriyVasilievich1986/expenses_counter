"""Address request schemas module."""

from .get_all_addresses_query import GetAllAddressesQuery
from .post_address_body import PostAddressBody
from .put_address_body import PutAddressBody

__all__ = ("GetAllAddressesQuery", "PostAddressBody", "PutAddressBody")
