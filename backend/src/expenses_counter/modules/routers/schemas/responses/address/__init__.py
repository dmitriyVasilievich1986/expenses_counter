"""Address responses schemas module."""

from .get_all import GetAllAddressesResponse, SimpleAddressGet
from .get_single import GetSingleAddressResponse, SimpleShopGet

__all__ = ("GetAllAddressesResponse", "GetSingleAddressResponse", "SimpleAddressGet", "SimpleShopGet")
